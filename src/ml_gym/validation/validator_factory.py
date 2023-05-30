from typing import Dict, Any, Type
from ml_gym.modes import RunMode, ValidationMode
from ml_gym.validation.nested_cross_validation import NestedCV
from ml_gym.validation.cross_validation import CrossValidation
from ml_gym.validation.gs_validator import GridSearchValidator, ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.error_handling.exception import ValidationModeNotValidError
import torch


class ValidatorFactory:
    """
    Validator Factory contains all the available validation stratergies.
    """
    @staticmethod
    def get_nested_cv(gs_config: Dict[str, Any], cv_config: Dict[str, Any], blue_print_type: Type[BluePrint],
                      run_mode: RunMode) -> NestedCV:
        """
        Get nested CV Validator
        :params:
            - gs_config (Dict[str, Any]): Grid Search Configuration.
            - cv_config (Dict[str, Any]): Cross Validation Configuration.
            - blue_print_type (Type[BluePrint]): BluePrint Type.
            - run_mode (RunMode): Validation Mode.
        
        :returns:
            NestedCV object: Initialized NestedCV object.
        """
        iterator_key = cv_config["NESTED_CROSS_VALIDATION"]["iterator_key"]
        split_key = cv_config["NESTED_CROSS_VALIDATION"]["split_key"]
        component_names = [iterator_key]
        components = blue_print_type.construct_components(config=gs_config, component_names=component_names)
        iterator = components[iterator_key][split_key]
        return NestedCV(dataset_iterator=iterator, **cv_config["NESTED_CROSS_VALIDATION"]["config"], run_mode=run_mode)

    @staticmethod
    def get_cross_validator(gs_config: Dict[str, Any], cv_config: Dict[str, Any], blue_print_type: Type[BluePrint],
                            run_mode: RunMode) -> CrossValidation:
        """
        Get Cross Validator
        :params:
            - gs_config (Dict[str, Any]): Grid Search Configuration.
            - cv_config (Dict[str, Any]): Cross Validation Configuration.
            - blue_print_type (Type[BluePrint]): BluePrint Type.
            - run_mode (RunMode): Validation Mode.
            
        :returns:
            CrossValidation object: Initialized CrossValidation object.
        """
        iterator_key = cv_config["CROSS_VALIDATION"]["iterator_key"]
        split_key = cv_config["CROSS_VALIDATION"]["split_key"]
        component_names = [iterator_key]
        components = blue_print_type.construct_components(config=gs_config, component_names=component_names,
                                                          device=torch.device("cpu"))
        iterator = components[iterator_key][split_key]
        return CrossValidation(dataset_iterator=iterator, **cv_config["CROSS_VALIDATION"]["config"], run_mode=run_mode)

    @staticmethod
    def get_gs_validator(run_mode: RunMode) -> GridSearchValidator:
        """
        Get Cross Validator
        :params:
            run_mode (RunMode): Validation Mode.         
        :returns:
            GridSearchValidator object: Initialized GridSearchValidator object.
        """
        return GridSearchValidator(run_mode=run_mode)


def get_validator(validation_mode: ValidationMode, blue_print_class:  Type[BluePrint],
                  run_mode: RunMode, cv_config: Dict = None, gs_config: Dict = None,) -> ValidatorIF:
    """
    Get Validator.
    :params:
        - validation_mode (ValidationMode): Validation Mode.
        - blue_print_class (Type[BluePrint]): BluePrint Type.
        - run_mode (RunMode): Validation Mode.
        - cv_config (Dict[str, Any]): Cross Validation Configuration.
        - gs_config (Dict[str, Any]): Grid Search Configuration.
    
    :returns:
        validator (ValidatorIF): Initialized validator stratergy.
    """
    if validation_mode == ValidationMode.GRID_SEARCH:
        validator = ValidatorFactory.get_gs_validator(run_mode=run_mode)
    elif validation_mode == ValidationMode.CROSS_VALIDATION:
        validator = ValidatorFactory.get_cross_validator(gs_config=gs_config,
                                                         cv_config=cv_config,
                                                         blue_print_type=blue_print_class,
                                                         run_mode=run_mode)
    elif validation_mode == ValidationMode.NESTED_CV:
        validator = ValidatorFactory.get_nested_cv(gs_config=gs_config,
                                                   cv_config=cv_config,
                                                   blue_print_type=blue_print_class,
                                                   run_mode=run_mode)
    else:
        raise ValidationModeNotValidError
    return validator
