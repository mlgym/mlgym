from typing import Dict, Any, Type
from ml_gym.blueprints.blue_prints import create_blueprint
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.util.grid_search import GridSearch


class GridSearchValidator(ValidatorIF):
    def __init__(self, grid_search_id: str, re_eval: bool = False):
        self.grid_search_id = grid_search_id
        self.re_eval = re_eval

    def run(self, blue_print_type: Type[BluePrint], gym: Gym, gs_config: Dict[str, Any],
            num_epochs: int, dashify_logging_path: str):
        run_id_to_config_dict = {run_id: config for run_id, config in enumerate(GridSearch.create_gs_from_config_dict(gs_config))}
        blueprints = []
        for config_id, experiment_config in run_id_to_config_dict.items():
            blueprint = create_blueprint(blue_print_class=blue_print_type,
                                         run_mode=AbstractGymJob.Mode.TRAIN if not self.re_eval else AbstractGymJob.Mode.EVAL,
                                         experiment_config=experiment_config,
                                         dashify_logging_path=dashify_logging_path,
                                         num_epochs=num_epochs,
                                         grid_search_id=self.grid_search_id,
                                         experiment_id=config_id)
            blueprints.append(blueprint)
        gym.add_blue_prints(blueprints)
        gym.run(parallel=True)
