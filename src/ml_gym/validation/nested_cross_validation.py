from typing import Dict, Any, Tuple, List, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.blueprints.blue_prints import BluePrint
from data_stack.dataset.splitter import SplitterFactory
from ml_gym.modes import RunMode
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.component_factory import Injector
from ml_gym.util.grid_search import GridSearch


class NestedCV(ValidatorIF):
    """
    Class containing functions to perform Nested Cross Validation.
    """
    def __init__(self, dataset_iterator: DatasetIteratorIF, num_outer_loop_folds: int,
                 num_inner_loop_folds: int, inner_stratification: bool, outer_stratification: bool,
                 target_pos: int, shuffle: bool, seed: int, run_mode: RunMode):
        self.num_outer_loop_folds = num_outer_loop_folds
        self.num_inner_loop_folds = num_inner_loop_folds
        self.inner_stratification = inner_stratification
        self.outer_stratification = outer_stratification
        self.dataset_iterator = dataset_iterator
        self.seed = seed
        self.target_pos = target_pos
        self.shuffle = shuffle
        self.run_mode = run_mode

    def _get_fold_indices(self) -> Tuple[List[int]]:
        splitter = SplitterFactory.get_nested_cv_splitter(num_inner_loop_folds=self.num_inner_loop_folds,
                                                          num_outer_loop_folds=self.num_outer_loop_folds,
                                                          inner_stratification=self.inner_stratification,
                                                          outer_stratification=self.outer_stratification,
                                                          target_pos=self.target_pos,
                                                          shuffle=self.shuffle,
                                                          seed=self.seed)
        indices = splitter.get_indices(dataset_iterator=self.dataset_iterator)
        return indices

    @staticmethod
    def _create_outer_folds_splits(outer_folds_indices: Tuple[List[int]]) -> List[Dict[str, Any]]:
        """
        Create Outer Fold Splits of nested CV.
        :params:
            outer_folds_indices (Tuple[List[int]]): List of Outer folds indicies.
        :returns:
            splits (List[Dict[str, Any]]): Outer fold Splits.
        """
        # outer folds
        # [outer_fold_1_indices, outer_fold2_indices ...]
        splits = []
        for outer_fold_id, test_fold_indices in enumerate(outer_folds_indices):
            # create train fold
            train_fold_indices = []
            for i, fold in enumerate(outer_folds_indices):
                if i != outer_fold_id:
                    train_fold_indices = train_fold_indices + fold

            split = {
                "id_outer_test_fold_id": outer_fold_id,
                "id_inner_test_fold_id": -1,
                "id_split_indices": {
                    "train": train_fold_indices,
                    "test": test_fold_indices
                }
            }
            splits.append(split)
        return splits

    @staticmethod
    def _create_inner_folds_splits(inner_folds_indices: Tuple[List[int]]) -> List[Dict[str, Any]]:
        """
        Create Inner Fold Splits of nested CV.
        :params:
            inner_folds_indices (Tuple[List[int]]): List of Inner folds indicies.
        :returns:
            splits (List[Dict[str, Any]]): Inner fold Splits.
        """
        splits = []
        # inner folds
        # [[outer_fold_1_inner_fold_1_indices, outer_fold_1_inner_fold_2_indices, ...], ...]
        for outer_fold_id, inner_folds in enumerate(inner_folds_indices):
            for inner_fold_id, test_fold_indices in enumerate(inner_folds):
                # calc train fold indices
                train_fold_indices = []
                for i, fold in enumerate(inner_folds):
                    if i != inner_fold_id:
                        train_fold_indices = train_fold_indices + fold
                split = {
                    "id_outer_test_fold_id": outer_fold_id,
                    "id_inner_test_fold_id": inner_fold_id,
                    "id_split_indices": {
                        "train": train_fold_indices,
                        "test": test_fold_indices
                    }
                }
                splits.append(split)
        return splits

    def _get_blue_prints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any]) -> List[Type[BluePrint]]:
        """
        Function to get a list of blueprints.
        :params:
               grid_search_id (str): Grid Search ID.
               blue_print_type (Type[BluePrint]): BluePrint Type.
               gs_config (Dict[str, Any]): Grid Search Configuration.
        
        :returns: 
            blueprints(List[Type[BluePrint]]) : List of blueprint objects.
        """
        run_id_to_config_dict = {run_id: config for run_id, config in enumerate(GridSearch.create_gs_from_config_dict(gs_config))}

        outer_fold_indices, inner_folds_indices = self._get_fold_indices()

        outer_splits = NestedCV._create_outer_folds_splits(outer_fold_indices)
        inner_splits = NestedCV._create_inner_folds_splits(inner_folds_indices)
        splits = outer_splits + inner_splits

        blueprints = []
        experiment_id = 0
        for split in splits:
            for config_id, experiment_config in run_id_to_config_dict.items():
                external_injection = {"id_experiment_id": experiment_id,
                                      "id_hyper_paramater_combination_id": config_id,
                                      **split}
                injector = Injector(mapping=external_injection)
                experiment_config_injected = injector.inject_pass(component_parameters=experiment_config)
                bp = BluePrint.create_blueprint(blue_print_class=blue_print_type,
                                                run_mode=self.run_mode,
                                                experiment_config=experiment_config_injected,
                                                grid_search_id=grid_search_id,
                                                experiment_id=experiment_id)
                blueprints.append(bp)
                experiment_id = experiment_id + 1
        return blueprints

    def create_blueprints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any]) -> List[BluePrint]:
        """
        Function to create a list of blueprints.
        :params:
               grid_search_id (str): Grid Search ID.
               blue_print_type (Type[BluePrint]): BluePrint Type.
               gs_config (Dict[str, Any]): Grid Search Configuration.
        
        :returns: 
            blueprints(List[BluePrint]) : List of blueprint objects.
        """
        blueprints = self._get_blue_prints(grid_search_id=grid_search_id,
                                           blue_print_type=blue_print_type,
                                           gs_config=gs_config)
        return blueprints
