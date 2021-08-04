from typing import Dict, Any, Type
from ml_gym.validation.nested_cross_validation import NestedCV
from ml_gym.validation.cross_validation import CrossValidation
from ml_gym.validation.gs_validator import GridSearchValidator
from ml_gym.blueprints.blue_prints import BluePrint


class ValidatorFactory:

    @staticmethod
    def get_nested_cv(gs_config: Dict[str, Any], cv_config: Dict[str, Any], grid_search_id: str,
                      blue_print_type: Type[BluePrint], re_eval: bool = False, keep_interim_results: bool = True) -> NestedCV:
        iterator_key = cv_config["NestedCV"]["iterator_key"]
        split_key = cv_config["NestedCV"]["split_key"]
        component_names = [iterator_key]
        components = blue_print_type.construct_components(config=gs_config, component_names=component_names)
        iterator = components[iterator_key][split_key]
        return NestedCV(dataset_iterator=iterator, grid_search_id=grid_search_id, **cv_config["NestedCV"]["config"], re_eval=re_eval,
                        keep_interim_results=keep_interim_results)

    @staticmethod
    def get_cross_validator(gs_config: Dict[str, Any], cv_config: Dict[str, Any], grid_search_id: str,
                            blue_print_type: Type[BluePrint], re_eval: bool = False, keep_interim_results: bool = True) -> CrossValidation:
        iterator_key = cv_config["CV"]["iterator_key"]
        split_key = cv_config["CV"]["split_key"]
        component_names = [iterator_key]
        components = blue_print_type.construct_components(config=gs_config, component_names=component_names)
        iterator = components[iterator_key][split_key]
        return CrossValidation(dataset_iterator=iterator, grid_search_id=grid_search_id, **cv_config["CV"]["config"], re_eval=re_eval,
                               keep_interim_results=keep_interim_results)

    @staticmethod
    def get_gs_validator(grid_search_id: str, re_eval: bool = False, keep_interim_results: bool = True) -> GridSearchValidator:
        return GridSearchValidator(grid_search_id=grid_search_id, re_eval=re_eval, keep_interim_results=keep_interim_results)
