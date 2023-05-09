from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym_jobs.accelerate_gym_job import AccelerateGymJob
from ml_gym.gym.gym_jobs.gym_job import AbstractGymJob
from ml_gym.gym.gym_jobs.standard_gym_job import StandardGymJob
from ml_gym.persistency.io import GridSearchAPIClientConstructable
from ml_gym.persistency.logging import ExperimentStatusLogger, MLgymStatusLoggerCollectionConstructable
import torch
from accelerate import Accelerator


class GymJobFactory:
    """
    Class used to create GymJob to work on single or multiple CPU/GPU.
    """

    @staticmethod
    def get_gym_job_from_blueprint(blueprint: BluePrint, device: torch.device, num_epochs: int,
                                   logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                                   gs_restful_api_client_constructable: GridSearchAPIClientConstructable,
                                   num_batches_per_epoch: int = None) -> AbstractGymJob:
        """
        Create Gym Job to be used on single CPU or GPU.
        :params:
            blueprint (BluePrint): Blueprint class object having all the components for the GymJob.\n
            device (torch.device): Torch device either CPUs or a specified GPU.\n
            num_epochs(int): number of epochs to be trained to.\n
            logger_collection_constructable (LoggerConstructableIF): Logging interface\n
            gs_restful_api_client_constructable (GridSearchAPIClientConstructableIF): Interface to initiate GridSearchAPIClient\n
            num_batches_per_epoch (int): Number of batches to be trained per epoch.
        """ 
        components = blueprint.construct(device)

        logger_collection = logger_collection_constructable.construct()
        experiment_status_logger = ExperimentStatusLogger(logger=logger_collection, grid_search_id=blueprint.grid_search_id,
                                                          experiment_id=blueprint.experiment_id)
        gs_api_client = gs_restful_api_client_constructable.construct()

        gym_job = StandardGymJob(run_mode=blueprint.run_mode,
                                 grid_search_id=blueprint.grid_search_id,
                                 experiment_id=blueprint.experiment_id,
                                 num_epochs=num_epochs,
                                 warm_start_epoch=blueprint.warm_start_epoch,
                                 experiment_status_logger=experiment_status_logger,
                                 gs_api_client=gs_api_client,
                                 num_batches_per_epoch=num_batches_per_epoch,
                                 **components)
        return gym_job

    @staticmethod
    def get_accelerate_gymjob_from_blueprint(blueprint: BluePrint, num_epochs: int,
                                             logger_collection_constructable: MLgymStatusLoggerCollectionConstructable,
                                             gs_restful_api_client_constructable: GridSearchAPIClientConstructable,
                                             accelerator: Accelerator,
                                             num_batches_per_epoch: int = None) -> AbstractGymJob:
        """
        Create Gym Job to be used on multiple GPUs using Accelerate.
        :params:
            blueprint (BluePrint): Blueprint class object having all the components for the GymJob.\n
            num_epochs(int): number of epochs to be trained to.\n
            logger_collection_constructable (LoggerConstructableIF): Logging interface\n
            gs_restful_api_client_constructable (GridSearchAPIClientConstructableIF): Interface to initiate GridSearchAPIClient\n
            accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.\n
            num_batches_per_epoch (int): Number of batches to be trained per epoch.
        """ 
        components = blueprint.construct()

        logger_collection = logger_collection_constructable.construct()
        experiment_status_logger = ExperimentStatusLogger(logger=logger_collection, grid_search_id=blueprint.grid_search_id,
                                                          experiment_id=blueprint.experiment_id)
        gs_api_client = gs_restful_api_client_constructable.construct()

        gym_job = AccelerateGymJob(run_mode=blueprint.run_mode,
                                   grid_search_id=blueprint.grid_search_id,
                                   experiment_id=blueprint.experiment_id,
                                   num_epochs=num_epochs,
                                   warm_start_epoch=blueprint.warm_start_epoch,
                                   experiment_status_logger=experiment_status_logger,
                                   gs_api_client=gs_api_client,
                                   num_batches_per_epoch=num_batches_per_epoch,
                                   accelerator=accelerator,
                                   **components)
        return gym_job
