"""
State manager for accessing Arena state from Web process.
Caches the latest state received from Arena via IPC.
"""
from typing import Any, Optional
import threading


class StateManager:
    """Manages cached Arena state in the Web process."""
    
    def __init__(self):
        self._state: dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def update_state(self, state: dict[str, Any]):
        """Update the cached state with new data from Arena."""
        with self._lock:
            self._state.update(state)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from the cached state."""
        with self._lock:
            return self._state.get(key, default)
    
    def get_all_state(self) -> dict[str, Any]:
        """Get a copy of all cached state."""
        with self._lock:
            return self._state.copy()


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def set_state_manager(manager: StateManager):
    """Set the global state manager instance."""
    global _state_manager
    _state_manager = manager
