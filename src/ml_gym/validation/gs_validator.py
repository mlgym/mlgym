from typing import Dict, Any, Type, List
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.modes import RunMode
from ml_gym.validation.validator import ValidatorIF
from ml_gym.util.grid_search import GridSearch


class GridSearchValidator(ValidatorIF):
    """
    Validator for Grid Search.
    """
    def __init__(self, run_mode: RunMode):
        self.run_mode = run_mode

    def create_blueprints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any]) -> List[BluePrint]:
        """
        Function to create a list of blueprints.
        :params:
           - grid_search_id (str): Grid Search ID.
           - blue_print_type (Type[BluePrint]): BluePrint Type.
           - gs_config (Dict[str, Any]): Grid Search Configuration.
        
        :returns: 
            blueprints(List[Type[BluePrint]]) : List of blueprint objects.
        """
        run_id_to_config_dict = {run_id: config for run_id, config in enumerate(GridSearch.create_gs_from_config_dict(gs_config))}

        blueprints = []
        for config_id, experiment_config in run_id_to_config_dict.items():
            blueprint = BluePrint.create_blueprint(blue_print_class=blue_print_type,
                                                   run_mode=self.run_mode,
                                                   experiment_config=experiment_config,
                                                   grid_search_id=grid_search_id,
                                                   experiment_id=config_id)
            blueprints.append(blueprint)
        return blueprints
