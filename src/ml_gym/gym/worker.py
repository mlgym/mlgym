from abc import ABC, abstractmethod
from ml_gym.gym.gym_jobs.standard_gym_job import AbstractGymJob


class WorkerIF(ABC):
    """
    Worker Interface
    """

    @abstractmethod
    def work(job: AbstractGymJob):
        pass


class Worker(WorkerIF):
    """
    Worker class providing function to run gym job.
    """

    def __init__(self):
        pass

    def work(job: AbstractGymJob):
        pass
