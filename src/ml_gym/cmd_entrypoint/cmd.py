import argparse
from dataclasses import dataclass
from datetime import datetime
from ml_board.backend.restful_api.data_models import FileFormat
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.error_handling.exception import GymError
from ml_gym.gym.gym import Gym, GymFactory
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable, LoggerConstructableIF, MLgymStatusLoggerConfig, \
    MLgymStatusLoggerTypes
from ml_gym.modes import RunMode, ValidationMode
from ml_gym.util.util import SystemEnv
from ml_gym.validation.validator_factory import get_validator
from ml_gym.io.config_parser import YAMLConfigLoader
from typing import Callable, List, Tuple, Type, Dict, Union
from ml_gym.persistency.io import GridSearchAPIClientConfig, GridSearchAPIClientConstructableIF, GridSearchAPIClientConstructable, \
    GridSearchAPIClientType
from pathlib import Path
import yaml
from accelerate import Accelerator
import json


@dataclass
class MultiProcessingEnvironmentConfig:
    process_count: int
    computation_device_ids: List[int]


@dataclass
class MainProcessEnvironmentConfig:
    computation_device_id: int


@dataclass
class AccelerateEnvironmentConfig:
    pass


@dataclass
class TrainRunConfiguration:
    num_epochs: int
    gs_config_path: str
    validation_config_path = None
    num_batches_per_epoch: int = None


@dataclass
class WarmStartRunConfiguration:
    gridsaerch_id: str
    num_epochs: int
    num_batches_per_epoch: int = None


@dataclass
class LoggingConfiguration:
    websocket_logging_servers: List[str]
    gs_rest_api_endpoint: str


def get_gym_from_environment_config(env_config: Union[MultiProcessingEnvironmentConfig, MainProcessEnvironmentConfig,
                                                      AccelerateEnvironmentConfig],
                                    logger_collection_constructable: LoggerConstructableIF,
                                    gs_restful_api_client_constructable: GridSearchAPIClientConstructableIF,
                                    num_epochs: int,
                                    num_batches_per_epoch: int = None,
                                    accelerator: Accelerator = None) -> Gym:

    if isinstance(env_config, MainProcessEnvironmentConfig):
        gym = GymFactory.get_sequential_gym(logger_collection_constructable=logger_collection_constructable,
                                            gs_restful_api_client_constructable=gs_restful_api_client_constructable,
                                            device_id=env_config.computation_device_id,
                                            num_batches_per_epoch=num_batches_per_epoch)
    elif isinstance(env_config, AccelerateEnvironmentConfig):
        gym = GymFactory.get_sequential_gym(logger_collection_constructable=logger_collection_constructable,
                                            gs_restful_api_client_constructable=gs_restful_api_client_constructable,
                                            num_epochs=num_epochs,
                                            num_batches_per_epoch=num_batches_per_epoch,
                                            accelerator=accelerator)
    elif isinstance(env_config, MultiProcessingEnvironmentConfig):
        gym = GymFactory.get_parallel_single_node_gym(logger_collection_constructable=logger_collection_constructable,
                                                      gs_restful_api_client_constructable=gs_restful_api_client_constructable,
                                                      process_count=env_config.process_count,
                                                      num_epochs=num_epochs,
                                                      device_ids=env_config.computation_device_ids,
                                                      num_batches_per_epoch=num_batches_per_epoch)
    else:
        raise GymError("Did not provide correct env_config")

    return gym


def get_logger_constructable(websocket_logging_servers: List) -> LoggerConstructableIF:
    websocket_logging_servers = [(f"{protocol}:{ip}", int(port)) for protocol, ip, port in [
        connection.split(":") for connection in websocket_logging_servers]]

    logging_configs = [MLgymStatusLoggerConfig(logger_type=MLgymStatusLoggerTypes.STREAMED_LOGGER, logger_config={"host": ip, "port": port})
                       for ip, port in websocket_logging_servers]
    logger_collection_constructable = MLgymStatusLoggerCollectionConstructable(logging_configs)
    return logger_collection_constructable


def get_grid_search_restful_api_client_constructable(endpoint: str) -> GridSearchAPIClientConstructableIF:
    client_config = GridSearchAPIClientConfig(api_client_type=GridSearchAPIClientType.GRID_SEARCH_RESTFUL_API_CLIENT,
                                              api_client_config={"endpoint": endpoint})
    client_constructable = GridSearchAPIClientConstructable(client_config)
    return client_constructable


def entry_train(gridsearch_id: str, blueprint_class: Type[BluePrint], gym: Gym, gs_config_path: str, run_config_path: str,
                validation_strategy_config_path: str, gs_restful_api_client_constructable: GridSearchAPIClientConstructableIF,
                accelerator: Accelerator = None):

    def log_configs(gs_config_string: str, run_config_string: str, validation_strategy_config_raw_string: str,
                    gs_restful_api_client_constructable: GridSearchAPIClientConstructableIF, accelerator: Accelerator = None):
        if accelerator is None or accelerator.is_main_process:
            gs_api_client = gs_restful_api_client_constructable.construct()
            gs_api_client.add_config_string(grid_search_id=gridsearch_id,
                                            file_format=FileFormat.YAML,
                                            config_name="grid_search_config.yml",
                                            config=gs_config_string)
            gs_api_client.add_config_string(grid_search_id=gridsearch_id, 
                                            file_format=FileFormat.YAML, 
                                            config_name="run_config.yml", 
                                            config=run_config_string)

            if validation_strategy_config_raw_string is not None:
                gs_api_client.add_config_string(grid_search_id=gridsearch_id,
                                                config_name="validation_strategy_config.yml",
                                                config=validation_strategy_config_raw_string)

            for blueprint in blueprints:
                gs_api_client.add_config_string(grid_search_id=blueprint.grid_search_id, config_name="experiment_config.json",
                                                config=json.dumps(blueprint.config), experiment_id=blueprint.experiment_id,
                                                file_format=FileFormat.JSON)
                gs_api_client.add_config_string(grid_search_id=blueprint.grid_search_id, config_name="system_info.json",
                                                config=json.dumps(SystemEnv.create_system_info()), experiment_id=blueprint.experiment_id,
                                                file_format=FileFormat.JSON)

    gs_config_string = Path(gs_config_path).read_text()
    gs_config = YAMLConfigLoader.load_string(gs_config_string)
    run_config_string = Path(run_config_path).read_text()

    if validation_strategy_config_path is not None:
        validation_strategy_config_string = Path(validation_strategy_config_path).read_text()
        validation_strategy_config = YAMLConfigLoader.load(validation_strategy_config_string)
        validation_mode = ValidationMode[list(validation_strategy_config.keys())[0]]
    else:
        validation_strategy_config_string = None
        validation_strategy_config = None
        validation_mode = ValidationMode.GRID_SEARCH

    gs_config = YAMLConfigLoader.load_string(gs_config_string)

    validator = get_validator(validation_mode, blueprint_class, RunMode.TRAIN, validation_strategy_config, gs_config)

    blueprints = validator.create_blueprints(grid_search_id=gridsearch_id,
                                             blue_print_type=blueprint_class,
                                             gs_config=gs_config)

    log_configs(gs_config_string=gs_config_string, run_config_string=run_config_string,      validation_strategy_config_raw_string=validation_strategy_config_string,
    gs_restful_api_client_constructable=gs_restful_api_client_constructable, accelerator=accelerator)

    gym.run(blueprints)


def entry_warm_start(blueprint_class: Type[BluePrint], gym: Gym, grid_search_id: int,
                     gs_restful_api_client_constructable: GridSearchAPIClientConstructableIF, num_epochs: int):

    gs_api_client = gs_restful_api_client_constructable.construct()
    experiment_statuses = gs_api_client.get_experiment_statuses(grid_search_id)

    blueprints = [BluePrint.create_blueprint(blue_print_class=blueprint_class,
                                             run_mode=RunMode.WARM_START,
                                             experiment_config=experiment_status.experiment_config,
                                             warm_start_epoch=experiment_status.last_checkpoint_id,
                                             grid_search_id=grid_search_id,
                                             experiment_id=experiment_status.experiment_id)
                  for experiment_status in experiment_statuses if experiment_status.last_checkpoint_id < num_epochs]

    gym.run(blueprints)


def get_args() -> Tuple[Callable, Dict]:
    parser = argparse.ArgumentParser(description='Run a grid search on CPUs or distributed over multiple GPUs')

    parser.add_argument('--config_path', type=str, required=True, help='Path to the run configuration file')

    args = parser.parse_args()
    return args.config_path


def parse_run_configuration(run_configuration_file_path: str) -> Tuple[Union[TrainRunConfiguration, WarmStartRunConfiguration],
                                                                       Union[MultiProcessingEnvironmentConfig, AccelerateEnvironmentConfig,
                                                                       MainProcessEnvironmentConfig], LoggingConfiguration]:
    with open(run_configuration_file_path, "r") as fp:
        run_configuration_dict = yaml.safe_load(fp)

    run_dict = run_configuration_dict["run_configuration"]
    environment_dict = run_configuration_dict["environment"]
    logging_dict = run_configuration_dict["logging"]

    if run_dict["type"] == "train":
        run_config = TrainRunConfiguration(**run_dict["config"])
    else:
        run_config = WarmStartRunConfiguration(**run_dict["config"])

    if environment_dict["type"] == "multiprocessing":
        environment_config = MultiProcessingEnvironmentConfig(**environment_dict["config"])
    elif environment_dict["type"] == "accelerate":
        environment_config = AccelerateEnvironmentConfig()
    else:
        environment_config = MainProcessEnvironmentConfig(**environment_dict["config"])

    logging_config = LoggingConfiguration(**logging_dict)

    return run_config, environment_config, logging_config


def get_logging_constructables(logging_config: LoggingConfiguration) -> Tuple[LoggerConstructableIF, GridSearchAPIClientConstructableIF]:
    # get logger constructables
    logger_collection_constructable = get_logger_constructable(logging_config.websocket_logging_servers)
    gs_restful_api_client_constructable = get_grid_search_restful_api_client_constructable(endpoint=logging_config.gs_rest_api_endpoint)
    return logger_collection_constructable, gs_restful_api_client_constructable


def run(blueprint_class: BluePrint, run_configuration_file_path):

    run_config, env_config, logging_config = parse_run_configuration(run_configuration_file_path=run_configuration_file_path)

    logger_collection_constructable, gs_restful_api_client_constructable = get_logging_constructables(logging_config)
    
    accelerator: Accelerator = Accelerator() if isinstance(env_config, AccelerateEnvironmentConfig) else None

    gym = get_gym_from_environment_config(env_config, logger_collection_constructable, gs_restful_api_client_constructable,
                                          run_config.num_epochs, run_config.num_batches_per_epoch, accelerator)


    if isinstance(run_config, TrainRunConfiguration):
        gridsearch_id = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        entry_train(gridsearch_id=gridsearch_id, blueprint_class=blueprint_class, gym=gym, gs_config_path=run_config.gs_config_path,
                    run_config_path=run_configuration_file_path, validation_strategy_config_path=run_config.validation_config_path,
                    gs_restful_api_client_constructable=gs_restful_api_client_constructable,
                    accelerator=accelerator)
    elif isinstance(run_config, WarmStartRunConfiguration):
        entry_warm_start(blueprint_class=blueprint_class, gym=gym, grid_search_id=run_config.gridsaerch_id,
                         gs_restful_api_client_constructable=gs_restful_api_client_constructable, num_epochs=run_config.num_epochs)
