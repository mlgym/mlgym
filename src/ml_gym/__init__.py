from datetime import datetime
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.gym.gym import Gym
from ml_gym.blueprints.blue_prints import BluePrint
from typing import List, Type
from ml_gym.util.grid_search import GridSearch
from ml_gym.util.logger import QueuedLogging
from multiprocessing import Queue


def create_gym(process_count: int, device_ids, log_std_to_file: bool) -> Gym:
    gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
    return gym


def setup_logging_environment(log_dir_path: str):
    queue = Queue()
    QueuedLogging.start_logging(queue, log_dir_path)


def stop_logging_environment():
    QueuedLogging.stop_listener()


def create_blueprints(blue_print_class: Type[BluePrint],
                      run_mode: AbstractGymJob.Mode,
                      gs_config_path: str,
                      dashify_logging_path: str,
                      num_epochs: int) -> List[BluePrint]:

    run_mode = AbstractGymJob.Mode[run_mode]
    run_id_to_config_dict = {str(run_id): config for run_id, config in enumerate(GridSearch.create_gs_configs_from_path(gs_config_path))}
    config_tuples = list(run_id_to_config_dict.items())
    epochs = list(range(num_epochs))
    grid_search_id = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    blueprints = []
    for run_id, config in config_tuples:
        blue_print = blue_print_class(grid_search_id=grid_search_id,
                                      run_id=run_id,
                                      epochs=epochs,
                                      run_mode=run_mode,
                                      config=config,
                                      dashify_logging_dir=dashify_logging_path)
        blueprints.append(blue_print)
    return blueprints
