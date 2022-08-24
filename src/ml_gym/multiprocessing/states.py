from enum import Enum, IntEnum


class JobType(IntEnum):
    CALC = 1
    TERMINATE = 2


class JobStatus(str, Enum):
    INIT = "INIT"
    RUNNING = "RUNNING"
    DONE = "DONE"
