import json
from typing import List, Type
from ml_board.backend.restful_api.data_models import FileFormat
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.modes import RunMode
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF, GridSearchAPIClientIF
from ml_gym.persistency.logging import LoggerConstructableIF, MLgymStatusLoggerCollectionConstructable
from ml_gym.util.logger import QueuedLogging
from multiprocessing import Queue
from ml_gym.validation.validator import ValidatorIF
from datetime import datetime
from ml_gym.io.config_parser import YAMLConfigLoader


class MLGymStarter:
    @staticmethod
    def _create_gym(job_id_prefix: str, process_count: int, device_ids, log_std_to_file: bool,
                    logger_collection_constructable: MLgymStatusLoggerCollectionConstructable) -> Gym:
        gym = Gym(job_id_prefix, process_count, device_ids=device_ids, log_std_to_file=log_std_to_file,
                  logger_collection_constructable=logger_collection_constructable)
        return gym

    @staticmethod
    def _setup_logging_environment(log_dir_path: str):
        if QueuedLogging._instance is None:
            queue = Queue()
            QueuedLogging.start_logging(queue, log_dir_path)

    @staticmethod
    def _stop_logging_environment():
        QueuedLogging.stop_listener()


# class MLGymTrainWarmStarter(MLGymStarter):

#     def __init__(self, grid_search_id: str, blue_print_class: Type[BluePrint], num_epochs: int, text_logging_path: str, process_count: int,
#                  gpus: List[int], log_std_to_file: bool, gs_api_client_constructable: GridSearchAPIClientConstructableIF,
#                  logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> None:
#         self.blue_print_class = blue_print_class
#         self.num_epochs = num_epochs
#         self.text_logging_path = text_logging_path
#         self.process_count = process_count
#         self.log_std_to_file = log_std_to_file
#         self.gpus = gpus
#         self.grid_search_id = grid_search_id
#         self.gs_api_client_constructable = gs_api_client_constructable
#         self.gs_api_client = gs_api_client_constructable.construct()
#         self.logger_collection_constructable = logger_collection_constructable

#     def start(self):
#         self._setup_logging_environment(self.text_logging_path)
#         gym = MLGymStarter._create_gym(process_count=self.process_count, device_ids=self.gpus, log_std_to_file=self.log_std_to_file,
#                                        logger_collection_constructable=self.logger_collection_constructable)

#         blueprints = self.validator.create_blueprints(blue_print_type=self.blue_print_class,
#                                                       gs_config=self.gs_config,
#                                                       num_epochs=self.num_epochs,
#                                                       logger_collection_constructable=self.logger_collection_constructable)

#         gym.add_blue_prints(blueprints)
#         gym.run(parallel=True)

#         self._stop_logging_environment()


class MLGymTrainStarter(MLGymStarter):

    def __init__(self, text_logging_path: str, process_count: int,
                 gpus: List[int], log_std_to_file: bool, blueprints: List[BluePrint],
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> None:
        self.text_logging_path = text_logging_path
        self.process_count = process_count
        self.log_std_to_file = log_std_to_file
        self.gpus = gpus
        self.blueprints = blueprints
        self.logger_collection_constructable = logger_collection_constructable

    def start(self):
        self._setup_logging_environment(self.text_logging_path)
        job_id_prefix = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

        gym = MLGymStarter._create_gym(job_id_prefix=job_id_prefix, process_count=self.process_count, device_ids=self.gpus,
                                       log_std_to_file=self.log_std_to_file,
                                       logger_collection_constructable=self.logger_collection_constructable)
        gym.add_blueprints(self.blueprints)
        gym.run(parallel=True)

        self._stop_logging_environment()


def save_blueprint_config(blueprint: BluePrint, gs_api_client: GridSearchAPIClientIF):
    gs_api_client.add_config_string(grid_search_id=blueprint.grid_search_id, config_name="experiment_config.json",
                                    config=json.dumps(blueprint.config), experiment_id=blueprint.experiment_id,
                                    file_format=FileFormat.JSON)


def mlgym_entry_train(blueprint_class: Type[BluePrint],
                      logger_collection_constructable: LoggerConstructableIF,
                      gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                      gs_config_raw_string: str,
                      validator: ValidatorIF,
                      text_logging_path: str,
                      process_count: int,
                      gpus: int,
                      log_std_to_file: bool,
                      num_epochs: int,
                      validation_strategy_config_raw_string: str = None):
    gs_api_client = gs_api_client_constructable.construct()

    grid_search_id = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    gs_config = YAMLConfigLoader.load_string(gs_config_raw_string)
    gs_api_client.add_config_string(grid_search_id=grid_search_id,
                                    file_format=FileFormat.YAML,
                                    config_name="grid_search_config.yml",
                                    config=gs_config_raw_string)

    if validation_strategy_config_raw_string is not None:
        gs_api_client.add_config_string(grid_search_id=grid_search_id,
                                        config_name="validation_strategy_config.yml",
                                        config=validation_strategy_config_raw_string)

    blueprints = validator.create_blueprints(grid_search_id=grid_search_id,
                                             blue_print_type=blueprint_class,
                                             gs_config=gs_config,
                                             num_epochs=num_epochs,
                                             gs_api_client_constructable=gs_api_client_constructable,
                                             logger_collection_constructable=logger_collection_constructable)

    for blueprint in blueprints:
        save_blueprint_config(blueprint=blueprint, gs_api_client=gs_api_client)

    starter = MLGymTrainStarter(text_logging_path=text_logging_path,
                                process_count=process_count,
                                gpus=gpus,
                                log_std_to_file=log_std_to_file,
                                blueprints=blueprints,
                                logger_collection_constructable=logger_collection_constructable)
    starter.start()


def mlgym_entry_warm_start(blueprint_class: Type[BluePrint],
                           grid_search_id: str,
                           logger_collection_constructable: LoggerConstructableIF,
                           gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                           text_logging_path: str,
                           process_count: int,
                           gpus: int,
                           log_std_to_file: bool,
                           num_epochs: int):
    gs_api_client = gs_api_client_constructable.construct()
    experiment_statuses = gs_api_client.get_experiment_statuses(grid_search_id)

    blueprints = [BluePrint.create_blueprint(blue_print_class=blueprint_class,
                                             run_mode=RunMode.WARM_START,
                                             experiment_config=experiment_status.experiment_config,
                                             num_epochs=num_epochs,
                                             warm_start_epoch=experiment_status.last_checkpoint_id,
                                             grid_search_id=grid_search_id,
                                             experiment_id=experiment_status.experiment_id,
                                             logger_collection_constructable=logger_collection_constructable,
                                             gs_api_client_constructable=gs_api_client_constructable)
                  for experiment_status in experiment_statuses if experiment_status.last_checkpoint_id < num_epochs]

    starter = MLGymTrainStarter(text_logging_path=text_logging_path,
                                process_count=process_count,
                                gpus=gpus,
                                log_std_to_file=log_std_to_file,
                                blueprints=blueprints,
                                logger_collection_constructable=logger_collection_constructable)
    starter.start()
