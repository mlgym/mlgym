from ml_gym.persistency.io import GridSearchAPIClientConstructable
from ml_gym.persistency.logging import JobStatusLogger, MLgymStatusLoggerCollectionConstructable
import torch
from typing import Callable, List
from ml_gym.multiprocessing.pool import Pool, Job
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym_jobs.standard_gym_job import GymJobFactory, AbstractGymJob, GymJobType
from ml_gym.util.devices import get_devices
import tqdm
from abc import ABC, abstractmethod
from enum import Enum


class Gym(ABC):
    def __init__(self, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                 gs_restful_api_client_constructable: GridSearchAPIClientConstructable):
        self.job_status_logger = JobStatusLogger(logger_collection_constructable.construct())
        self.gs_restful_api_client_constructable = gs_restful_api_client_constructable

    @abstractmethod
    def run(self, blueprints: List[BluePrint]):
        """Executes the jobs. Note that this function blocks until all jobs have been executed!
        """
        raise NotImplementedError

    def get_jobs_from_blueprints(self, blueprints: List[BluePrint], exec_fun: Callable) -> List[Job]:
        jobs = []
        for job_id, blueprint in enumerate(blueprints):
            job = Job(job_id=f"{blueprint.grid_search_id}-{job_id}", fun=exec_fun, blueprint=blueprint)
            jobs.append(job)
            self.job_status_logger.log_experiment_config(grid_search_id=blueprint.grid_search_id,
                                                         experiment_id=blueprint.experiment_id,
                                                         job_id=job_id,
                                                         config=blueprint.config)
        return jobs

    @staticmethod
    def _run_standard_gym_job(blueprint: BluePrint, device: torch.device):
        gym_job = GymJobFactory.get_gym_job_from_blueprint(blueprint, device=device)
        return gym_job.execute(device=device)

    @staticmethod
    def _run_accelerate_gym_job(blueprint: BluePrint):
        gym_job = GymJobFactory.get_hf_accelerate_gymjob_from_blueprint(blueprint)
        return gym_job.execute()


class ParallelSingleNodeGym(Gym):
    def __init__(self, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                 gs_restful_api_client_constructable: GridSearchAPIClientConstructable,
                 process_count: int = 1, device_ids: List[int] = None):
        super().__init__(logger_collection_constructable, gs_restful_api_client_constructable)
        self.devices = get_devices(device_ids)
        self.pool = Pool(num_processes=process_count, devices=self.devices, logger_collection_constructable=logger_collection_constructable)

    def run(self, blueprints: List[BluePrint]):
        """Executes the jobs. Note that this function blocks until all jobs have been executed!
        """
        torch.multiprocessing.set_start_method('spawn', force=True)
        jobs = self.get_jobs_from_blueprints(blueprints, exec_fun=Gym._run_standard_gym_job)
        for job in jobs:
            self.pool.add_job(job)
        self.pool.run()


class SequentialGym(Gym):
    def __init__(self, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                 gs_restful_api_client_constructable: GridSearchAPIClientConstructable,
                 exec_fun: Callable):
        super().__init__(logger_collection_constructable, gs_restful_api_client_constructable)
        self.exec_fun = exec_fun

    def run(self, blueprints: List[BluePrint]):
        """Executes the jobs. Note that this function blocks until all jobs have been executed!
        """

        jobs = self.get_jobs_from_blueprints(blueprints)
        for job in tqdm.tqdm(jobs, desc="Models trained"):
            self.exec_fun(job)
        self.job_status_logger.disconnect()

    def work(self, job: Job):
        # we don't set the device in job because every job executed on the main thread should be handled via accelerate
        job.execute()


class GymType(Enum):
    SEQUENTIAL_GYM = SequentialGym
    PARALLEL_SINGLE_NODE_GYM = ParallelSingleNodeGym


class GymFactory:

    @staticmethod
    def get_sequential_gym(job_id_prefix: str, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable) -> Gym:
        exec_fun = SequentialGym._run_accelerate_gym_job
        return SequentialGym(job_id_prefix=job_id_prefix, logger_collection_constructable=logger_collection_constructable,
                             exec_fun=exec_fun)

    @staticmethod
    def get_parallel_single_node_gym(job_id_prefix: str, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                                     process_count: int = 1, device_ids: List[int] = None) -> Gym:
        return ParallelSingleNodeGym(job_id_prefix=job_id_prefix, logger_collection_constructable=logger_collection_constructable,
                                     process_count=process_count, device_ids=device_ids)
