from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.blueprints.blue_prints import BluePrint
from typing import List, Type, Dict, Any
from ml_gym.util.grid_search import GridSearch


def create_blueprints(blue_print_class: Type[BluePrint],
                      run_mode: AbstractGymJob.Mode,
                      gs_config: Dict[str, Any],
                      dashify_logging_path: str,
                      num_epochs: int,
                      grid_search_id: str,
                      external_injection: Dict[str, Any] = None,
                      initial_experiment_id: int = 0) -> List[BluePrint]:

    run_id_to_config_dict = {run_id: config for run_id, config in enumerate(
        GridSearch.create_gs_from_config_dict(gs_config))}
    config_tuples = list(run_id_to_config_dict.items())
    epochs = list(range(num_epochs))

    blueprints = []
    for run_id, config in config_tuples:
        blue_print = blue_print_class(grid_search_id=grid_search_id,
                                      run_id=str(run_id + initial_experiment_id),
                                      epochs=epochs,
                                      run_mode=run_mode,
                                      config=config,
                                      dashify_logging_dir=dashify_logging_path,
                                      external_injection=external_injection)
        blueprints.append(blue_print)
    return blueprints
