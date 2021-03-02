from typing import Dict, Any, Type
from ml_gym import create_blueprints
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint


class GridSearchValidator(ValidatorIF):
    def __init__(self, grid_search_id: str):
        self.grid_search_id = grid_search_id

    def run(self, blue_print_type: Type[BluePrint], gym: Gym, gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        blueprints = create_blueprints(blue_print_class=blue_print_type,
                                       run_mode=AbstractGymJob.Mode.TRAIN,
                                       gs_config=gs_config,
                                       dashify_logging_path=dashify_logging_path,
                                       num_epochs=num_epochs, 
                                       grid_search_id=self.grid_search_id)
        gym.add_blue_prints(blueprints)
        gym.run(parallel=True)
