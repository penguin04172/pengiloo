from multiprocessing import Queue
from typing import Optional

# Global variable to hold the IPC queue in the WebServer process
event_queue: Optional[Queue] = None
command_queue: Optional[Queue] = None


def set_event_queue(queue: Queue):
    global event_queue
    event_queue = queue


def get_event_queue() -> Optional[Queue]:
    return event_queue


def set_command_queue(queue: Queue):
    global command_queue
    command_queue = queue


def get_command_queue() -> Optional[Queue]:
    return command_queue
