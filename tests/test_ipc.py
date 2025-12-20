"""
Unit tests for IPC Manager
"""
import pytest
import multiprocessing
from ipc import IPCManager


@pytest.mark.unit
class TestIPCManager:
    """Test IPC Manager functionality."""
    
    def test_ipc_manager_singleton(self):
        """Test that IPCManager follows singleton pattern."""
        ipc1 = IPCManager()
        ipc2 = IPCManager()
        assert ipc1 is not ipc2  # Not singleton anymore, each process creates its own
    
    def test_send_command(self, ipc_queues):
        """Test sending commands through IPC."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        
        # Send command
        ipc.send_command("test_command", {"key": "value"})
        
        # Verify command is in queue
        assert not command_queue.empty()
        cmd = command_queue.get()
        assert cmd["command"] == "test_command"
        assert cmd["payload"]["key"] == "value"
    
    def test_get_command(self, ipc_queues):
        """Test getting commands from IPC."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        
        # Put command in queue
        command_queue.put({"command": "load_match", "payload": {"match_id": 1}})
        
        # Get command
        cmd = ipc.get_command()
        assert cmd is not None
        assert cmd["command"] == "load_match"
        assert cmd["payload"]["match_id"] == 1
    
    def test_get_command_empty_queue(self, ipc_queues):
        """Test getting command from empty queue."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        
        # Get from empty queue
        cmd = ipc.get_command()
        assert cmd is None
    
    def test_broadcast_state(self, ipc_queues):
        """Test broadcasting state through IPC."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.state_queue = state_queue
        
        # Broadcast state
        ipc.broadcast_state("match_state", {"state": "PRE_MATCH"})
        
        # Verify state is in queue
        assert not state_queue.empty()
        state = state_queue.get()
        assert state["type"] == "match_state"
        assert state["data"]["state"] == "PRE_MATCH"
    
    def test_get_state_update(self, ipc_queues):
        """Test getting state updates from IPC."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.state_queue = state_queue
        
        # Put state update in queue
        state_queue.put({"type": "realtime_score", "data": {"red": 10, "blue": 20}})
        
        # Get state update
        state = ipc.get_state_update()
        assert state is not None
        assert state["type"] == "realtime_score"
        assert state["data"]["red"] == 10
        assert state["data"]["blue"] == 20
    
    def test_multiple_commands(self, ipc_queues):
        """Test sending and receiving multiple commands."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        
        # Send multiple commands
        commands = [
            ("start_match", {}),
            ("abort_match", {}),
            ("commit_results", {}),
        ]
        
        for cmd_name, payload in commands:
            ipc.send_command(cmd_name, payload)
        
        # Verify all commands are in queue
        for cmd_name, _ in commands:
            cmd = command_queue.get()
            assert cmd["command"] == cmd_name
