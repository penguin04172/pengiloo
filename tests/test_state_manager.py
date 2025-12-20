"""
Unit tests for State Manager
"""
import pytest
from web.state_manager import get_state_manager, set_state_manager, StateManager


@pytest.mark.unit
class TestStateManager:
    """Test State Manager functionality."""
    
    def test_state_manager_singleton(self):
        """Test that StateManager is a singleton."""
        manager1 = get_state_manager()
        manager2 = get_state_manager()
        assert manager1 is manager2
    
    def test_update_state(self):
        """Test updating state."""
        manager = get_state_manager()
        
        state_dict = {"match_state": "PRE_MATCH"}
        manager.update_state(state_dict)
        assert manager.get_state("match_state") == "PRE_MATCH"
    
    def test_update_multiple_states(self):
        """Test updating multiple states."""
        manager = get_state_manager()
        
        states = {
            "match_id": 123,
            "match_state": "AUTO_PERIOD",
            "match_time_sec": 15,
        }
        
        manager.update_state(states)
        
        assert manager.get_state("match_id") == 123
        assert manager.get_state("match_state") == "AUTO_PERIOD"
        assert manager.get_state("match_time_sec") == 15
    
    def test_get_state_default(self):
        """Test getting state with default value."""
        # Create fresh manager for this test
        manager = StateManager()
        
        value = manager.get_state("nonexistent_key", "default_value")
        assert value == "default_value"
    
    def test_get_all_state(self):
        """Test getting all state."""
        manager = StateManager()
        
        manager.update_state({"key1": "value1"})
        manager.update_state({"key2": "value2"})
        
        all_state = manager.get_all_state()
        assert "key1" in all_state
        assert "key2" in all_state
        assert all_state["key1"] == "value1"
        assert all_state["key2"] == "value2"
    
    def test_thread_safety(self):
        """Test thread safety of state manager."""
        import threading
        
        manager = StateManager()
        
        def update_state(key, value):
            for i in range(100):
                manager.update_state({key: f"{value}_{i}"})
        
        threads = [
            threading.Thread(target=update_state, args=(f"key_{i}", f"value_{i}"))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all keys are present
        all_state = manager.get_all_state()
        assert len(all_state) == 10
