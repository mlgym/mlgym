from typing import Dict, Any, Type, List
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.modes import RunMode
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable
from ml_gym.validation.validator import ValidatorIF
from ml_gym.util.grid_search import GridSearch
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF


class GridSearchValidator(ValidatorIF):
    def __init__(self, run_mode: RunMode):
        self.run_mode = run_mode

    def create_blueprints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any], num_epochs: int,
                          gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                          logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> List[BluePrint]:
        run_id_to_config_dict = {run_id: config for run_id, config in enumerate(GridSearch.create_gs_from_config_dict(gs_config))}

        blueprints = []
        for config_id, experiment_config in run_id_to_config_dict.items():
            blueprint = BluePrint.create_blueprint(blue_print_class=blue_print_type,
                                                   run_mode=self.run_mode,
                                                   experiment_config=experiment_config,
                                                   num_epochs=num_epochs,
                                                   grid_search_id=grid_search_id,
                                                   experiment_id=config_id,
                                                   logger_collection_constructable=logger_collection_constructable,
                                                   gs_api_client_constructable=gs_api_client_constructable)
            blueprints.append(blueprint)
        return blueprints
