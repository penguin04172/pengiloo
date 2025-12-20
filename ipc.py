import multiprocessing
from typing import Any, Optional

class IPCManager:
    _instance = None
    
    def __init__(self):
        self.command_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.state_queue: multiprocessing.Queue = multiprocessing.Queue()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def send_command(self, command: str, payload: Any = None):
        self.command_queue.put({"command": command, "payload": payload})

    def get_command(self) -> Optional[dict]:
        if not self.command_queue.empty():
            return self.command_queue.get()
        return None

    def broadcast_state(self, state_type: str, data: Any):
        self.state_queue.put({"type": state_type, "data": data})

    def get_state_update(self) -> Optional[dict]:
        if not self.state_queue.empty():
            return self.state_queue.get()
        return None
