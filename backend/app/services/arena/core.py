import time
import queue
from multiprocessing import Queue
from loguru import logger
from backend.app.services.arena.models import ArenaState


class ArenaController:
    def __init__(self, event_queue: Queue, command_queue: Queue):
        self.event_queue = event_queue
        self.command_queue = command_queue
        self.state = ArenaState.IDLE
        self.last_update_time = time.time()

        # Timer variables
        self.timer_running = False
        self.remaining_time = 0.0

        # Configuration (Defaults, should be loaded from Event DB later)
        self.config = {
            "auto_duration": 15,
            "pause_duration": 3,
            "teleop_duration": 135,
            "warning_remaining": 20,
        }

    def update(self):
        """Main loop update called by the process loop."""
        # Process Commands
        try:
            while True:
                cmd = self.command_queue.get_nowait()
                self._handle_command(cmd)
        except queue.Empty:
            pass

        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if self.timer_running:
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self._handle_timer_expired()

            # We can throttle this if needed, but for local network 60Hz/30Hz is usually fine
            # For now, let's just publish on state changes or every second to avoid flooding logs/ws
            # In production, we want high frequency timer updates.
            pass

    def _handle_command(self, cmd: dict):
        logger.info(f"Arena received command: {cmd}")
        action = cmd.get("action")
        if action == "START":
            self.start_match()
        elif action == "ABORT":
            self.abort_match()
        elif action == "RESET":
            self.reset_match()
        else:
            logger.warning(f"Unknown command action: {action}")

    def _handle_timer_expired(self):
        self.timer_running = False
        if self.state == ArenaState.AUTO:
            self.transition_to(ArenaState.PAUSE)
        elif self.state == ArenaState.PAUSE:
            self.transition_to(ArenaState.TELEOP)
        elif self.state == ArenaState.TELEOP:
            self.transition_to(ArenaState.END)
        elif self.state == ArenaState.TIMEOUT:
            self.transition_to(ArenaState.IDLE)

    def transition_to(self, new_state: ArenaState):
        logger.info(f"Arena Transition: {self.state} -> {new_state}")
        self.state = new_state

        # State Entry Logic
        if new_state == ArenaState.IDLE:
            self.timer_running = False
            self.remaining_time = 0

        elif new_state == ArenaState.PRE_START:
            self.timer_running = False
            self.remaining_time = 0

        elif new_state == ArenaState.AUTO:
            self.remaining_time = self.config["auto_duration"]
            self.timer_running = True
            # Trigger Start Sound

        elif new_state == ArenaState.PAUSE:
            self.remaining_time = self.config["pause_duration"]
            self.timer_running = True
            # Trigger Auto End Sound

        elif new_state == ArenaState.TELEOP:
            self.remaining_time = self.config["teleop_duration"]
            self.timer_running = True
            # Trigger Teleop Start Sound

        elif new_state == ArenaState.END:
            self.timer_running = False
            self.remaining_time = 0
            # Trigger Match End Sound

        elif new_state == ArenaState.ESTOP:
            self.timer_running = False
            # Cut power immediately

        self.publish_status()

    def start_match(self):
        if self.state == ArenaState.PRE_START or self.state == ArenaState.IDLE:
            self.transition_to(ArenaState.AUTO)
        else:
            logger.warning(f"Cannot start match from state {self.state}")

    def abort_match(self):
        self.transition_to(ArenaState.ESTOP)

    def reset_match(self):
        self.transition_to(ArenaState.IDLE)

    def publish_status(self):
        status = {
            "type": "arena_status",
            "state": self.state.value,
            "remaining_time": int(self.remaining_time),  # Send int for display
            "timestamp": time.time(),
        }
        try:
            self.event_queue.put(status)
        except Exception as e:
            logger.error(f"Failed to publish arena status: {e}")
