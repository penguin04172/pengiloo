import multiprocessing
import uvicorn
import time
from loguru import logger
from backend.app.core import ipc


def run_web_server(event_queue, command_queue):
    """Function to run the FastAPI server in a separate process."""
    logger.info("Starting Web Server Process...")

    # Initialize the IPC queue for this process
    ipc.set_event_queue(event_queue)
    ipc.set_command_queue(command_queue)

    # Import here to avoid circular imports or side effects in main process
    # reload=False is important for multiprocessing stability in production-like modes
    uvicorn.run(
        "backend.app.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


def run_arena_core(stop_event, event_queue, command_queue):
    """Function to run the Arena Control logic."""
    logger.info("Starting Arena Core Process...")

    # Import here to avoid pickling issues with multiprocessing
    from backend.app.services.arena.core import ArenaController

    controller = ArenaController(event_queue, command_queue)

    # Simulation removed - now controlled via API

    while not stop_event.is_set():
        controller.update()

        # Publish status periodically (e.g., 10Hz)
        # In a real scenario, we might want to publish only on change or at a fixed rate
        # controller.publish_status() # This is now called inside transition_to

        # We can also add a periodic heartbeat/time sync here
        if controller.timer_running:
            # Publish time every second
            if int(time.time() * 10) % 10 == 0:
                controller.publish_status()

        time.sleep(0.1)  # 10Hz Loop

    logger.info("Arena Core Process Stopping...")


def main():
    logger.info("Initializing FRC FMS System...")

    # Multiprocessing setup
    # Windows requires 'spawn', Linux uses 'fork' by default but 'spawn' is safer for cross-platform consistency
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass  # Context might already be set

    stop_event = multiprocessing.Event()
    event_queue = multiprocessing.Queue()
    command_queue = multiprocessing.Queue()

    # Create processes
    web_process = multiprocessing.Process(
        target=run_web_server, args=(event_queue, command_queue), name="WebServer"
    )
    arena_process = multiprocessing.Process(
        target=run_arena_core,
        args=(stop_event, event_queue, command_queue),
        name="ArenaCore",
    )

    processes = [web_process, arena_process]

    try:
        for p in processes:
            p.start()

        logger.success("All systems operational. Press Ctrl+C to exit.")

        # Main loop monitoring
        while True:
            time.sleep(1)
            if not web_process.is_alive():
                logger.warning("Web server process died!")
                break
            if not arena_process.is_alive():
                logger.warning("Arena core process died!")
                break

    except KeyboardInterrupt:
        logger.info("Shutdown signal received...")
    finally:
        stop_event.set()
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()
        logger.info("System Shutdown Complete.")


if __name__ == "__main__":
    main()
