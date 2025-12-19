from enum import Enum


class ArenaState(str, Enum):
    IDLE = "IDLE"
    PRE_START = "PRE_START"
    AUTO = "AUTO"
    PAUSE = "PAUSE"
    TELEOP = "TELEOP"
    END = "END"
    POST_MATCH = "POST_MATCH"
    TIMEOUT = "TIMEOUT"
    ESTOP = "ESTOP"
