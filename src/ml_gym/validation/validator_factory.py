from typing import Dict, Any
from ml_gym.validation.nested_cross_validation import NestedCV
from ml_gym.gym.gym import Gym
from ml_gym.blueprints.component_factory import ComponentFactory


class ValidatorFactory:

    @staticmethod
    def get_nested_cv(gym: Gym, gs_config: Dict[str, Any], cv_config: Dict[str, Any]):
        iterator_key = cv_config["NestedCV"]["iterator_key"]
        component_names = [iterator_key]
        component_factory = ComponentFactory()
        components = component_factory.build_components_from_config(gs_config, component_names)
        iterator = components[iterator_key]
        return NestedCV(gym=gym, dataset_iterator=iterator, **cv_config["NestedCV"]["config"])
