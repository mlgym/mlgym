from enum import IntEnum, Enum
import torch
from typing import Callable, Dict, List


class JobType(IntEnum):
    CALC = 1
    TERMINATE = 2


class JobStatus(str, Enum):
    INIT = "INIT"
    RUNNING = "RUNNING"
    DONE = "DONE"


class Job:
    def __init__(self, job_id: int, fun: Callable, param_dict: Dict, job_type: JobType = JobType.CALC):
        self.job_id = job_id
        self.job_type = job_type
        self.fun = fun
        self.param_dict = param_dict

        self.status = JobStatus.INIT
        self.starting_time = -1
        self.finishing_time = -1
        self.executing_process_id = -1
        self.error = None
        self.stacktrace = None
        self._device: torch.device = None

    @property
    def device(self) -> torch.device:
        return self._device

    @device.setter
    def device(self, value: torch.device):
        self._device = value

    def execute(self):
        self.param_dict["device"] = self._device
        return self.fun(**self.param_dict)


class JobStatusSubscriberIF:

    def callback_job_event(self, job: Job):
        raise NotImplementedError


class JobCollection:

    def __init__(self):
        self.job_dict: Dict[str, Job] = {}
        self.subscribers: List[JobStatusSubscriberIF] = []

    def add_or_update_job(self, job: Job):
        self.job_dict[job.job_id] = job
        self.update_subscribers(job)

    def add_subscriber(self, subscriber: JobStatusSubscriberIF):
        self.subscribers.append(subscriber)

    def update_subscribers(self, job: Job):
        for s in self.subscribers:
            s.callback_job_event(job)

    def __len__(self) -> int:
        return len(self.job_dict)

    @property
    def done(self) -> bool:
        return all([job.status == JobStatus.DONE for job in self.job_dict.values()])

    @property
    def done_count(self) -> bool:
        return sum([job.status == JobStatus.DONE for job in self.job_dict.values()])

    @property
    def job_count(self) -> int:
        return len(self.job_dict)
