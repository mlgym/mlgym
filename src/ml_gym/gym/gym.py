import torch
from dashify.logging.dashify_logging import ExperimentTracking
from typing import List
from ml_gym.multiprocessing.pool import Pool, Job
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.jobs import AbstractGymJob
from functools import partial
from ml_gym.util.devices import get_devices
import tqdm

torch.multiprocessing.set_start_method('spawn', force=True)


class Gym:
    def __init__(self, process_count: int = 1, device_ids: List[int] = None, log_std_to_file: bool = True):
        self.devices = get_devices(device_ids)
        self.log_std_to_file = log_std_to_file
        self.pool = Pool(num_processes=process_count, devices=self.devices)
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

    def add_blue_print(self, blue_print: BluePrint):
        job = Job(job_id=len(self.jobs), fun=Gym._run_job, param_dict={"blue_print": blue_print, "log_std_to_file": self.log_std_to_file})
        self.jobs.append(job)

    def add_blue_prints(self, blue_prints: List[BluePrint]):
        for blue_print in blue_prints:
            self.add_blue_print(blue_print)

    @staticmethod
    def _run_job(blue_print: BluePrint, device: torch.device, log_std_to_file: bool) -> AbstractGymJob:
        gym_job = AbstractGymJob.from_blue_print(blue_print)
        decorated_runner = ExperimentTracking(gym_job.experiment_info, log_to_file=log_std_to_file)(partial(gym_job.execute, device=device))
        decorated_runner(device=device)
        return gym_job

    def work(self, device: torch.device):
        for job in tqdm.tqdm(self.jobs, desc="Models trained"):
            job.device = device
            job.execute()
