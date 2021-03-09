from typing import Dict, Any, Tuple, List, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.blueprints.blue_prints import create_blueprint
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from data_stack.dataset.splitter import SplitterFactory
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.blueprints.component_factory import Injector
from ml_gym.util.grid_search import GridSearch


class NestedCV(ValidatorIF):
    def __init__(self, dataset_iterator: DatasetIteratorIF, num_outer_loop_folds: int,
                 num_inner_loop_folds: int, inner_stratification: bool, outer_stratification: bool,
                 target_pos: int, shuffle: bool, grid_search_id: str, seed: int):
        self.num_outer_loop_folds = num_outer_loop_folds
        self.num_inner_loop_folds = num_inner_loop_folds
        self.inner_stratification = inner_stratification
        self.outer_stratification = outer_stratification
        self.dataset_iterator = dataset_iterator
        self.seed = seed
        self.grid_search_id = grid_search_id
        self.target_pos = target_pos
        self.shuffle = shuffle

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

    def create_blue_prints(self, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any], num_epochs: int,
                           dashify_logging_path: str) -> List[Type[BluePrint]]:

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
                bp = create_blueprint(blue_print_class=blue_print_type,
                                      run_mode=AbstractGymJob.Mode.TRAIN,
                                      experiment_config=experiment_config_injected,
                                      dashify_logging_path=dashify_logging_path,
                                      num_epochs=num_epochs,
                                      grid_search_id=self.grid_search_id,
                                      experiment_id=experiment_id)
                blueprints.append(bp)
                experiment_id = experiment_id + 1
        return blueprints

    def run(self, blue_print_type: Type[BluePrint], gym: Gym, gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        blueprints = self.create_blue_prints(blue_print_type=blue_print_type,
                                             gs_config=gs_config,
                                             dashify_logging_path=dashify_logging_path,
                                             num_epochs=num_epochs)
        gym.add_blue_prints(blueprints)
        gym.run(parallel=True)
