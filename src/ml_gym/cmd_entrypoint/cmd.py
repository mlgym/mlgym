import argparse
from datetime import datetime
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import GymFactory
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable, LoggerConstructableIF, MLgymStatusLoggerConfig, \
    MLgymStatusLoggerTypes
from ml_gym.modes import RunMode, ValidationMode
from ml_gym.starter import get_blueprints_train, get_blueprints_warmstart
from ml_gym.validation.validator_factory import get_validator
from ml_gym.io.config_parser import YAMLConfigLoader
from typing import Callable, List, Tuple, Type, Dict
from ml_gym.persistency.io import GridSearchAPIClientConfig, GridSearchAPIClientConstructableIF, GridSearchAPIClientConstructable, \
    GridSearchAPIClientType
from pathlib import Path


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


def entry_train(blueprint_class: Type[BluePrint], websocket_logging_servers: List[str],  gs_rest_api_endpoint: str, gs_config_path: str,
                validation_strategy_config_path: str, process_count: int, gpus: List[int], num_epochs: int):
    logger_collection_constructable = get_logger_constructable(websocket_logging_servers)
    gs_restful_api_client_constructable = get_grid_search_restful_api_client_constructable(endpoint=gs_rest_api_endpoint)

    gs_config_string = Path(gs_config_path).read_text()
    gs_config = YAMLConfigLoader.load_string(gs_config_string)

    if validation_strategy_config_path is not None:
        validation_strategy_config_string = Path(validation_strategy_config_path).read_text()
        validation_strategy_config = YAMLConfigLoader.load(validation_strategy_config_string)
        validation_mode = ValidationMode[list(validation_strategy_config.keys())[0]]
    else:
        validation_strategy_config_string = None
        validation_strategy_config = None
        validation_mode = ValidationMode.GRID_SEARCH

    validator = get_validator(validation_mode, blueprint_class, RunMode.TRAIN, validation_strategy_config, gs_config)

    blueprints = get_blueprints_train(blueprint_class=blueprint_class,
                                      logger_collection_constructable=logger_collection_constructable,
                                      gs_api_client_constructable=gs_restful_api_client_constructable,
                                      gs_config_raw_string=gs_config_string,
                                      validation_strategy_config_raw_string=validation_strategy_config_string,
                                      validator=validator,
                                      process_count=process_count,
                                      gpus=gpus,
                                      num_epochs=num_epochs)

    job_id_prefix = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    # TODO select the correct gym
    gym = GymFactory.get_sequential_gym(job_id_prefix=job_id_prefix, logger_collection_constructable=logger_collection_constructable,
                                        gs_restful_api_client_constructable=gs_restful_api_client_constructable)
    gym.run(blueprints)


def entry_warm_start(blueprint_class: Type[BluePrint], websocket_logging_servers: List[str], gs_rest_api_endpoint: str,
                     grid_search_id: str, process_count: int, gpus: List[int], num_epochs: int):
    logger_collection_constructable = get_logger_constructable(websocket_logging_servers)
    gs_restful_api_client_constructable = get_grid_search_restful_api_client_constructable(endpoint=gs_rest_api_endpoint)

    blueprints = get_blueprints_warmstart(blueprint_class=blueprint_class,
                                          grid_search_id=grid_search_id,
                                          logger_collection_constructable=logger_collection_constructable,
                                          gs_api_client_constructable=gs_restful_api_client_constructable,
                                          process_count=process_count,
                                          gpus=gpus,
                                          num_epochs=num_epochs)
    
    # TODO select the correct gym
    gym = GymFactory.get_sequential_gym(job_id_prefix=grid_search_id, logger_collection_constructable=logger_collection_constructable,
                                        gs_restful_api_client_constructable=gs_restful_api_client_constructable)
    gym.run(blueprints)



def get_args() -> Tuple[Callable, Dict]:
    parser = argparse.ArgumentParser(description='Run a grid search on CPUs or distributed over multiple GPUs')

    subparsers = parser.add_subparsers(help='Mutually exclusive arguments for TRAIN and WARM_START')

    # Train
    parser_train = subparsers.add_parser('train', help='Trains the models from scratch')
    parser_train.set_defaults(run_mode_function=entry_train)
    parser_train.add_argument('--gs_config_path', type=str, required=True, help='Path to the grid search config')
    parser_train.add_argument('--validation_strategy_config_path', type=str, required=False, help='Path to the validation strategy config')

    # Warmstart
    parser_warm_start = subparsers.add_parser('warm_start', help='Starts off from a previously started grid search')
    parser_warm_start.set_defaults(run_mode_function=entry_warm_start)
    parser_warm_start.add_argument('--grid_search_id', type=str, required=True, help='Gridsearch id identifying the specific grid search')

    # single node multi GPU gym
    parser.add_argument('--process_count', type=int, required=True, help='Max. number of processes running at a time.')
    parser.add_argument('--gpus', type=int, nargs='+', help='Indices of GPUs to distribute the GS over', default=None)

    # SEQUENTIAL_GS_SINGLE_NODE_DISTRIBUTED
    # TODO

    # Common
    parser.add_argument('--num_epochs', type=int, required=True, help='Number of epoch')
    parser.add_argument('--websocket_logging_servers', type=str, nargs='+',
                        help='List of websocket logging servers, e.g., 127.0.0.1:9090 127.0.0.1:8080', default=None)
    parser.add_argument('--gs_rest_api_endpoint', type=str, required=True,
                        help='Endpoint for the grid search API, e.g., 127.0.0.1:8080')
    # parser.add_argument('--validation_mode', choices=['NESTED_CROSS_VALIDATION', 'GRID_SEARCH', 'CROSS_VALIDATION'], required=True)

    args = parser.parse_args()
    run_mode_function = args.run_mode_function
    args_dict = vars(args)
    args_dict.pop("run_mode_function")
    return run_mode_function, args_dict


def run(run_mode_function: Callable, blueprint_class: BluePrint, args):

    # gym = ....

    run_mode_function(blueprint_class=blueprint_class, **args)
