"""
Unit tests for Arena State and Arena Commands
"""
import pytest
from web import arena_state, arena_commands
from web.arena import APIArena
from ipc import IPCManager


@pytest.mark.unit
class TestArenaState:
    """Test Arena State helper functions."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup state manager for each test."""
        from web.state_manager import get_state_manager, StateManager, set_state_manager
        # Create new manager for each test to avoid state leakage
        manager = StateManager()
        set_state_manager(manager)
        yield
    
    def test_get_match_state_default(self):
        """Test getting match state with default."""
        state = arena_state.get_match_state()
        assert state == "PRE_MATCH"  # Default value
    
    def test_get_match_id(self):
        """Test getting match ID."""
        from web.state_manager import get_state_manager
        get_state_manager().update_state({"match_id": 42})
        
        match_id = arena_state.get_match_id()
        assert match_id == 42
    
    def test_get_match_id_none(self):
        """Test getting match ID when None."""
        match_id = arena_state.get_match_id()
        assert match_id is None
    
    def test_get_realtime_score(self):
        """Test getting realtime score."""
        from web.state_manager import get_state_manager
        red_score_data = {"score": 100, "fouls": []}
        blue_score_data = {"score": 90, "fouls": []}
        get_state_manager().update_state({"red_score": red_score_data, "blue_score": blue_score_data})
        
        red_score = arena_state.get_realtime_score("red")
        blue_score = arena_state.get_realtime_score("blue")
        assert red_score["score"] == 100
        assert blue_score["score"] == 90
    
    def test_get_alliance_stations(self):
        """Test getting alliance stations."""
        from web.state_manager import get_state_manager
        stations_data = {
            "R1": {"team_id": 1234, "bypass": False},
            "B1": {"team_id": 5678, "bypass": False},
        }
        get_state_manager().update_state({"alliance_stations": stations_data})
        
        stations = arena_state.get_alliance_stations()
        assert stations["R1"]["team_id"] == 1234
        assert stations["B1"]["team_id"] == 5678


@pytest.mark.unit
class TestArenaCommands:
    """Test Arena Commands."""
    
    @pytest.fixture(autouse=True)
    def setup(self, ipc_queues):
        """Setup IPC for each test."""
        command_queue, state_queue = ipc_queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        ipc.state_queue = state_queue
        APIArena.set_ipc(ipc)
        self.command_queue = command_queue
        yield
    
    def test_load_match_command(self):
        """Test load match command."""
        arena_commands.load_match(42)
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "load_match"
        assert cmd["payload"]["match_id"] == 42
    
    def test_start_match_command(self):
        """Test start match command."""
        arena_commands.start_match()
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "start_match"
    
    def test_abort_match_command(self):
        """Test abort match command."""
        arena_commands.abort_match()
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "abort_match"
    
    def test_commit_results_command(self):
        """Test commit results command."""
        arena_commands.commit_scores()
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "commit_scores"
    
    def test_set_audience_display_command(self):
        """Test set audience display command."""
        arena_commands.set_audience_display("match")
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "set_audience_display"
        assert cmd["payload"]["mode"] == "match"
    
    def test_add_foul_command(self):
        """Test add foul command."""
        arena_commands.add_foul("red", True)
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "add_foul"
        assert cmd["payload"]["alliance"] == "red"
        assert cmd["payload"]["is_major"] is True
    
    def test_update_foul_command(self):
        """Test update foul command."""
        arena_commands.update_foul("blue", "update_foul_team", 0, 1234, 0)
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "update_foul"
        assert cmd["payload"]["alliance"] == "blue"
        assert cmd["payload"]["command"] == "update_foul_team"
        assert cmd["payload"]["index"] == 0
        assert cmd["payload"]["team_id"] == 1234
    
    def test_assign_card_command(self):
        """Test assign card command."""
        arena_commands.assign_card("red", 1234, "yellow")
        
        cmd = self.command_queue.get()
        assert cmd["command"] == "assign_card"
        assert cmd["payload"]["alliance"] == "red"
        assert cmd["payload"]["team_id"] == 1234
        assert cmd["payload"]["card"] == "yellow"
