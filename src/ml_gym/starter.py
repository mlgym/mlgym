import json
from typing import List, Type
from ml_board.backend.restful_api.data_models import FileFormat
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.modes import RunMode
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF, GridSearchAPIClientIF
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable
from ml_gym.validation.validator import ValidatorIF
from datetime import datetime
from ml_gym.io.config_parser import YAMLConfigLoader


class MLGymTrainStarter:

    def __init__(self, process_count: int, gpus: List[int], blueprints: List[BluePrint],
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> None:
        self.process_count = process_count
        self.gpus = gpus
        self.blueprints = blueprints
        self.logger_collection_constructable = logger_collection_constructable

    def start(self):
        gym = MLGymTrainStarter._create_gym(process_count=self.process_count, device_ids=self.gpus,
                                            logger_collection_constructable=self.logger_collection_constructable)
        gym.add_blueprints(self.blueprints)
        gym.run(parallelization_mode=self.parallelization_mode)

    @staticmethod
    def _create_gym(process_count: int, device_ids,
                    logger_collection_constructable: MLgymStatusLoggerCollectionConstructable) -> Gym:
        gym = Gym(process_count=process_count, device_ids=device_ids,
                  logger_collection_constructable=logger_collection_constructable)
        return gym


def get_blueprints_train(gridsearch_id: int,
                         blueprint_class: Type[BluePrint],
                         gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                         gs_config_raw_string: str,
                         validator: ValidatorIF,
                         validation_strategy_config_raw_string: str = None):

    def save_blueprint_config(blueprint: BluePrint, gs_api_client: GridSearchAPIClientIF):
        gs_api_client.add_config_string(grid_search_id=blueprint.grid_search_id, config_name="experiment_config.json",
                                        config=json.dumps(blueprint.config), experiment_id=blueprint.experiment_id,
                                        file_format=FileFormat.JSON)

    gs_api_client = gs_api_client_constructable.construct()

    gs_config = YAMLConfigLoader.load_string(gs_config_raw_string)
    gs_api_client.add_config_string(grid_search_id=gridsearch_id,
                                    file_format=FileFormat.YAML,
                                    config_name="grid_search_config.yml",
                                    config=gs_config_raw_string)

    if validation_strategy_config_raw_string is not None:
        gs_api_client.add_config_string(grid_search_id=gridsearch_id,
                                        config_name="validation_strategy_config.yml",
                                        config=validation_strategy_config_raw_string)

    blueprints = validator.create_blueprints(grid_search_id=gridsearch_id,
                                             blue_print_type=blueprint_class,
                                             gs_config=gs_config)

    for blueprint in blueprints:
        save_blueprint_config(blueprint=blueprint, gs_api_client=gs_api_client)

    return blueprints


def get_blueprints_warmstart(blueprint_class: Type[BluePrint],
                             grid_search_id: str,
                             gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                             num_epochs: int):
    gs_api_client = gs_api_client_constructable.construct()
    experiment_statuses = gs_api_client.get_experiment_statuses(grid_search_id)

    blueprints = [BluePrint.create_blueprint(blue_print_class=blueprint_class,
                                             run_mode=RunMode.WARM_START,
                                             experiment_config=experiment_status.experiment_config,
                                             warm_start_epoch=experiment_status.last_checkpoint_id,
                                             grid_search_id=grid_search_id,
                                             experiment_id=experiment_status.experiment_id)
                  for experiment_status in experiment_statuses if experiment_status.last_checkpoint_id < num_epochs]
    return blueprints
