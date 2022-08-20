from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable
import torch
from typing import Dict, List
from ml_gym.multiprocessing.pool import Pool, Job
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.util.devices import get_devices
import tqdm


torch.multiprocessing.set_start_method('spawn', force=True)


class Gym:
    def __init__(self, process_count: int = 1, device_ids: List[int] = None, log_std_to_file: bool = True,
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None):
        self.devices = get_devices(device_ids)
        self.logger_collection_constructable = logger_collection_constructable
        self.log_std_to_file = log_std_to_file
        self.pool = Pool(num_processes=process_count, devices=self.devices, logger_collection_constructable=logger_collection_constructable)
        self.jobs: List[Job] = []

    def run(self, parallel=True):
        """Executes the jobs. Note that this function blocks until all jobs have been executed!

        Args:
            parallel (bool, optional): When set to True, jobs are run in parallel in the multiprocessing environment. Defaults to True.
        """
        if parallel:
            for job in self.jobs:
                self.pool.add_job(job)
            self.pool.run()
        else:
            self.work(self.devices[0])

    def add_blue_print(self, blue_print: BluePrint) -> int:
        job = Job(job_id=len(self.jobs), fun=Gym._run_job, blue_print=blue_print, param_dict={"log_std_to_file": self.log_std_to_file})
        self.jobs.append(job)
        return job.job_id

    def add_blue_prints(self, blue_prints: List[BluePrint]):
        job_id_to_blueprint: Dict[int, BluePrint] = {}
        for blue_print in blue_prints:
            job_id = self.add_blue_print(blue_print)
            job_id_to_blueprint[job_id] = blue_print
        # TODO @PriyaTomar
        # send blueprints (i.e., job_id -> config)

    @staticmethod
    def _run_job(blue_print: BluePrint, device: torch.device, log_std_to_file: bool) -> AbstractGymJob:
        gym_job = AbstractGymJob.from_blue_print(blue_print)
        # decorated_runner = ExperimentTracking(gym_job.experiment_info, log_to_file=log_std_to_file)(partial(gym_job.execute, device=device))
        # decorated_runner(device=device)
        return gym_job.execute(device=device)

    def work(self, device: torch.device):
        for job in tqdm.tqdm(self.jobs, desc="Models trained"):
            job.device = device
            job.execute()
