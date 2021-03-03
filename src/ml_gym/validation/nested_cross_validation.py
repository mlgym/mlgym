from typing import Dict, Any, Tuple, List, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym import create_blueprints
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from data_stack.dataset.splitter import SplitterFactory
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.blueprints.component_factory import Injector


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

    def _create_blue_prints(self, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        outer_fold_indices, inner_folds_indices = self._get_fold_indices()
        blueprints = []
        # outer folds
        # [outer_fold_1_indices, outer_fold2_indices ...]
        for outer_fold_id, test_fold_indices in enumerate(outer_fold_indices):
            train_fold_indices = []
            for i, fold in enumerate(outer_fold_indices):
                if i != outer_fold_id:
                    train_fold_indices = train_fold_indices + fold

            external_injection = {
                "id_split_indices": {
                    "train": train_fold_indices,
                    "test": test_fold_indices
                },
                "id_fold_tags": {"outer_test_fold_id": outer_fold_id,
                                 "inner_test_fold_id": -1}
            }
            injector = Injector(mapping=external_injection)
            gs_config_injected = injector.inject_pass(component_parameters=gs_config)
            bp = create_blueprints(blue_print_class=blue_print_type,
                                   run_mode=AbstractGymJob.Mode.TRAIN,
                                   gs_config=gs_config_injected,
                                   dashify_logging_path=dashify_logging_path,
                                   num_epochs=num_epochs,
                                   # external_injection=external_injection,
                                   grid_search_id=self.grid_search_id,
                                   initial_experiment_id=len(blueprints))
            blueprints = blueprints + bp

        # inner folds
        # [[outer_fold_1_inner_fold_1_indices, outer_fold_1_inner_fold_2_indices, ...], ...]
        for outer_fold_id, folds in enumerate(inner_folds_indices):
            for inner_fold_id, test_fold_indices in enumerate(folds):
                # calc train fold indices
                train_fold_indices = []
                for i, fold in enumerate(folds):
                    if i != inner_fold_id:
                        train_fold_indices = train_fold_indices + fold

                external_injection = {
                    "id_split_indices": {
                        "train": train_fold_indices,
                        "test": test_fold_indices
                    },
                    "id_fold_tags": {"outer_test_fold_id": outer_fold_id,
                                     "inner_test_fold_id": inner_fold_id}
                }
                injector = Injector(mapping=external_injection)
                gs_config_injected = injector.inject_pass(component_parameters=gs_config)
                bp = create_blueprints(blue_print_class=blue_print_type,
                                       run_mode=AbstractGymJob.Mode.TRAIN,
                                       gs_config=gs_config_injected,
                                       dashify_logging_path=dashify_logging_path,
                                       num_epochs=num_epochs,
                                       # external_injection=external_injection,
                                       grid_search_id=self.grid_search_id,
                                       initial_experiment_id=len(blueprints))
                blueprints = blueprints + bp
        return blueprints

    def run(self, blue_print_type: Type[BluePrint], gym: Gym, gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        blueprints = self._create_blue_prints(blue_print_type=blue_print_type,
                                              gs_config=gs_config,
                                              dashify_logging_path=dashify_logging_path,
                                              num_epochs=num_epochs)
        gym.add_blue_prints(blueprints)
        gym.run(parallel=True)
