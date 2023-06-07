from enum import Enum, IntEnum


class JobType(IntEnum):
    """
    Job Type Enum to show current type of job being performed.
    """
    CALC = 1
    TERMINATE = 2


class JobStatus(str, Enum):
    """
    JobStatus Enum to represent the status of the Job.
    """
    INIT = "INIT"
    RUNNING = "RUNNING"
    DONE = "DONE"
