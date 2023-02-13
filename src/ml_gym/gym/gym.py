from ml_gym.persistency.logging import JobStatusLogger, MLgymStatusLoggerCollectionConstructable
import torch
from typing import List
from ml_gym.multiprocessing.pool import Pool, Job
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.util.devices import get_devices
import tqdm


torch.multiprocessing.set_start_method('spawn', force=True)


class Gym:
    def __init__(self, job_id_prefix: str, logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                 process_count: int = 1, device_ids: List[int] = None):
        self.devices = get_devices(device_ids)
        self.job_status_logger = JobStatusLogger(logger_collection_constructable.construct())
        self.pool = Pool(num_processes=process_count, devices=self.devices, logger_collection_constructable=logger_collection_constructable)
        self.jobs: List[Job] = []
        self.job_id_prefix = job_id_prefix
        self.job_counter = 0

    def run(self, parallel=True):
        """Executes the jobs. Note that this function blocks until all jobs have been executed!

        Args:
            parallel (bool, optional): When set to True, jobs are run in parallel in the multiprocessing environment. Defaults to True.
        """
        if parallel:
            for _ in range(len(self.jobs)):
                job = self.jobs.pop(0)
                self.pool.add_job(job)

            self.pool.run()
        else:
            for _ in tqdm.tqdm(range(len(self.jobs)), desc="Models trained"):
                job = self.jobs.pop(0)
                self.work(job, self.devices[0])

    def add_blueprint(self, blueprint: BluePrint) -> int:
        job = Job(job_id=f"{blueprint.grid_search_id}-{self.job_counter}", fun=Gym._run_job, blueprint=blueprint)
        self.job_counter += 1
        self.jobs.append(job)
        return job.job_id

    def add_blueprints(self, blueprints: List[BluePrint]):
        for blueprint in blueprints:
            job_id = self.add_blueprint(blueprint)
            self.job_status_logger.log_experiment_config(grid_search_id=blueprint.grid_search_id,
                                                         experiment_id=blueprint.experiment_id,
                                                         job_id=job_id,
                                                         config=blueprint.config)

    @staticmethod
    def _run_job(blueprint: BluePrint, device: torch.device) -> AbstractGymJob:
        gym_job = AbstractGymJob.from_blue_print(blueprint, device=device)
        return gym_job.execute(device=device)

    def work(self, job: Job, device: torch.device):
        job.device = device
        job.execute()
