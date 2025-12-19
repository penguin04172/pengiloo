from typing import Any

# Placeholder for IPC-based Arena communication
# The Web process no longer has direct access to the Arena instance


class APIArena:
    """
    API layer for communicating with Arena process via IPC.
    This replaces the singleton pattern with command-based communication.
    """
    _ipc = None

    @classmethod
    def set_ipc(cls, ipc):
        """Set the IPC manager instance for communicating with Arena."""
        cls._ipc = ipc

    @classmethod
    def get_ipc(cls):
        """Get the IPC manager instance."""
        if cls._ipc is None:
            raise ValueError('IPC is not initialized yet!')
        return cls._ipc

    @classmethod
    def send_command(cls, command: str, payload: Any = None):
        """Send a command to the Arena process."""
        if cls._ipc:
            cls._ipc.send_command(command, payload)

    @classmethod
    def get_state_update(cls):
        """Get the latest state update from Arena process."""
        if cls._ipc:
            return cls._ipc.get_state_update()
        return None


# Legacy compatibility function - will be refactored in web routes
def get_arena():
    """
    Deprecated: Direct Arena access is no longer available.
    Use APIArena.send_command() and APIArena.get_state_update() instead.
    """
    raise NotImplementedError(
        'Direct Arena access is not available in multiprocessing mode. '
        'Use APIArena for IPC-based communication.'
    )
