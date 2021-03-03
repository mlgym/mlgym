from typing import Dict, Any
from ml_gym.validation.nested_cross_validation import NestedCV
from ml_gym.validation.gs_validator import GridSearchValidator
from ml_gym.blueprints.component_factory import ComponentFactory


class ValidatorFactory:

    @staticmethod
    def get_nested_cv(gs_config: Dict[str, Any], cv_config: Dict[str, Any], grid_search_id: str):
        iterator_key = cv_config["NestedCV"]["iterator_key"]
        split_key = cv_config["NestedCV"]["split_key"]
        component_names = [iterator_key]
        component_factory = ComponentFactory()
        components = component_factory.build_components_from_config(gs_config, component_names)
        iterator = components[iterator_key][split_key]
        return NestedCV(dataset_iterator=iterator, grid_search_id=grid_search_id, **cv_config["NestedCV"]["config"])

    @staticmethod
    def get_gs_validator(grid_search_id: str):
        return GridSearchValidator(grid_search_id=grid_search_id)
