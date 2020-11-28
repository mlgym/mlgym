from enum import Enum
import torch
from typing import Callable, Dict


class JobType(Enum):
    CALC = 1
    TERMINATE = 2


class Job:
    def __init__(self, job_id: int, fun: Callable, param_dict: Dict, job_type: JobType = JobType.CALC):
        self.job_id = job_id
        self.job_type = job_type
        self.fun = fun
        self.param_dict = param_dict

        self.done = False
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
