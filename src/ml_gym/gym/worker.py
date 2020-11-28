from abc import ABC, abstractmethod
from ml_gym.gym.jobs import AbstractGymJob


class WorkerIF(ABC):

    @abstractmethod
    def work(job: AbstractGymJob):
        pass


class Worker(WorkerIF):

    def __init__(self):
        pass

    def work(job: AbstractGymJob):
        pass
