from abc import abstractmethod
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.multiprocessing.states import JobStatus, JobType
import torch
from typing import Callable, Dict, List


class JobIF:
    """
    Job Interface having important properties and execute function.
    """

    @property
    def experiment_id(self) -> str:
        raise NotImplementedError

    @property
    def grid_search_id(self) -> str:
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError


class Job(JobIF):
    """
    Class to initialzie Job with all meta data.
    """
    def __init__(self, job_id: str, fun: Callable, blueprint: BluePrint, param_dict: Dict = None, job_type: JobType = JobType.CALC):
        self.job_id = job_id
        self.job_type = job_type
        self.fun = fun
        self.blueprint = blueprint
        self.param_dict = param_dict if param_dict is not None else {}
        self.status = JobStatus.INIT
        self.starting_time = -1
        self.finishing_time = -1
        self.executing_process_id = -1
        self.error = None
        self.stacktrace = None

    @property
    def experiment_id(self) -> str:
        if self.blueprint is not None:
            return self.blueprint.experiment_id
        else:
            return None

    @property
    def grid_search_id(self) -> str:
        if self.blueprint is not None:
            return self.blueprint.grid_search_id
        else:
            return None

    def execute(self, device: torch.device = None):
        if device is not None:
            return self.fun(blueprint=self.blueprint, device=device, **self.param_dict)
        else:
            return self.fun(blueprint=self.blueprint, **self.param_dict)


class JobStatusSubscriberIF:

    @abstractmethod
    def callback_job_event(self, job: Job):
        raise NotImplementedError


class JobCollection:

    def __init__(self):
        self.job_dict: Dict[str, Job] = {}
        self.subscribers: List[JobStatusSubscriberIF] = []

    def add_or_update_job(self, job: Job):
        self.job_dict[job.job_id] = job
        if job.job_type == JobType.CALC:
            self.update_subscribers(job)

    def add_subscriber(self, subscriber: JobStatusSubscriberIF):
        self.subscribers.append(subscriber)

    def update_subscribers(self, job: Job):
        for s in self.subscribers:
            s.callback_job_event(job)

    def __len__(self) -> int:
        return len([1 for job in self.job_dict.values() if job.job_type == JobType.CALC])

    @property
    def done(self) -> bool:
        return all([job.status == JobStatus.DONE for job in self.job_dict.values() if job.job_type == JobType.CALC])

    @property
    def done_count(self) -> bool:
        return sum([job.status == JobStatus.DONE for job in self.job_dict.values() if job.job_type == JobType.CALC])

    @property
    def job_count(self) -> int:
        return len([1 for job in self.job_dict.values() if job.job_type == JobType.CALC])
