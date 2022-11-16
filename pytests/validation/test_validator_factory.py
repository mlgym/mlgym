from datetime import datetime
from typing import Any, Dict, Type
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.validation.cross_validation import CrossValidation
from ml_gym.validation.gs_validator import GridSearchValidator
from ml_gym.validation.nested_cross_validation import NestedCV
from ml_gym.validation.validator_factory import ValidatorFactory
from pytests.test_env.validation_fixtures import ValidationFixtures


class TestValidatorFactory(ValidationFixtures):
    def test_get_nested_cv(self, gs_nested_cv_config: Dict[str, Any], nested_cv_config: Dict[str, Any],
                           blue_print_type: Type[BluePrint], grid_search_id: str, re_eval: bool = False,
                           keep_interim_results: bool = True):
        nested_cv = ValidatorFactory.get_nested_cv(gs_config=gs_nested_cv_config,
                                                   cv_config=nested_cv_config,
                                                   grid_search_id=grid_search_id,
                                                   blue_print_type=blue_print_type,
                                                   re_eval=re_eval,
                                                   keep_interim_results=keep_interim_results)
        assert isinstance(nested_cv, NestedCV)

    def test_get_cross_validator(self, gs_cv_config: Dict[str, Any], cv_config: Dict[str, Any],
                                 blue_print_type: Type[BluePrint], grid_search_id: str,
                                 keep_interim_results: bool = True):
        cross_validator = ValidatorFactory.get_cross_validator(gs_config=gs_cv_config,
                                                               cv_config=cv_config,
                                                               grid_search_id=grid_search_id,
                                                               blue_print_type=blue_print_type,
                                                               re_eval=False,
                                                               keep_interim_results=keep_interim_results)
        assert isinstance(cross_validator, CrossValidation)

    def test_get_gs_validator(self, re_eval: bool = False, keep_interim_results: bool = True):
        gs_validator = ValidatorFactory.get_gs_validator(grid_search_id=datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
                                                         re_eval=re_eval, keep_interim_results=keep_interim_results)
        assert isinstance(gs_validator, GridSearchValidator)