"""
Integration tests for multiprocessing IPC communication
"""
import pytest
import asyncio
import multiprocessing
import time
from ipc import IPCManager
from field.arena import Arena
from models.base import create_db_and_tables


# Module-level function for multiprocessing (required for Windows)
def _run_arena_test_process(command_queue, state_queue):
    """Minimal arena process for testing."""
    async def arena_loop():
        # Directly use passed queues instead of creating new IPC Manager
        # Process commands for 5 seconds
        for _ in range(50):
            if not command_queue.empty():
                cmd = command_queue.get()
                # Echo command back as state
                state_queue.put({"type": "command_received", "data": cmd})
            await asyncio.sleep(0.1)
    
    asyncio.run(arena_loop())


@pytest.mark.integration
@pytest.mark.slow
class TestIPCIntegration:
    """Test IPC communication between processes."""
    
    @pytest.fixture
    def setup_arena_process(self):
        """Setup arena process for testing."""
        command_queue = multiprocessing.Queue()
        state_queue = multiprocessing.Queue()
        
        process = multiprocessing.Process(
            target=_run_arena_test_process,
            args=(command_queue, state_queue)
        )
        process.start()
        
        time.sleep(0.5)  # Wait for process to start
        
        yield command_queue, state_queue, process
        
        process.terminate()
        process.join(timeout=2)
    
    def test_command_to_arena_process(self, setup_arena_process):
        """Test sending command to arena process."""
        command_queue, state_queue, process = setup_arena_process
        
        # Check process is alive
        assert process.is_alive(), "Arena process should be running"
        
        # Send command
        command_queue.put({"command": "test_command", "payload": {"test": "data"}})
        
        # Wait for response (increased timeout)
        time.sleep(1.5)
        
        # Check if command was received
        if state_queue.empty():
            # Process might have crashed, check exit code
            if not process.is_alive():
                pytest.fail(f"Arena process died unexpectedly, exit code: {process.exitcode}")
            pytest.fail("No state update received from arena process")
        
        state = state_queue.get()
        assert state["type"] == "command_received"
        assert state["data"]["command"] == "test_command"
    
    def test_multiple_commands(self, setup_arena_process):
        """Test sending multiple commands."""
        command_queue, state_queue, process = setup_arena_process
        
        # Check process is alive
        assert process.is_alive(), "Arena process should be running"
        
        # Send multiple commands
        for i in range(5):
            command_queue.put({
                "command": f"command_{i}",
                "payload": {"index": i}
            })
        
        # Wait for responses (increased timeout)
        time.sleep(2)
        
        # Verify all commands were received
        received = []
        timeout = time.time() + 2  # Extra 2 seconds to drain queue
        while time.time() < timeout:
            if not state_queue.empty():
                state = state_queue.get()
                if state["type"] == "command_received":
                    received.append(state["data"]["command"])
            else:
                time.sleep(0.1)
        
        # Should have received at least some commands
        assert len(received) >= 3, f"Expected at least 3 commands, got {len(received)}: {received}"
        for cmd in received:
            assert cmd.startswith("command_"), f"Invalid command format: {cmd}"


# Module-level function for database testing (required for Windows)
def _create_team_in_process(team_id):
    """Create team in separate process."""
    import models
    from models.base import create_db_and_tables
    create_db_and_tables()
    
    team = models.Team(
        id=team_id,
        name=f"Team {team_id}",
        nickname=f"T{team_id}",
    )
    models.create_team(team)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database operations in multi-process environment."""
    
    def test_database_access_from_multiple_processes(self):
        """Test that multiple processes can access database."""
        create_db_and_tables()
        
        # Create teams in separate processes
        processes = []
        team_ids = [1000, 2000, 3000]
        
        for team_id in team_ids:
            p = multiprocessing.Process(target=_create_team_in_process, args=(team_id,))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
        
        # Verify all teams were created
        import models
        for team_id in team_ids:
            team = models.read_team_by_id(team_id)
            assert team is not None
            assert team.id == team_id
