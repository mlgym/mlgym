from typing import Dict, Any, List, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.blueprints.blue_prints import create_blueprint
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from data_stack.dataset.splitter import SplitterFactory
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.blueprints.component_factory import Injector
from ml_gym.util.grid_search import GridSearch


class CrossValidation(ValidatorIF):
    def __init__(self, dataset_iterator: DatasetIteratorIF, num_folds: int, stratification: bool,
                 target_pos: int, shuffle: bool, grid_search_id: str, seed: int, re_eval: bool = False,
                 keep_interim_results: bool = True):
        self.num_folds = num_folds
        self.stratification = stratification
        self.dataset_iterator = dataset_iterator
        self.seed = seed
        self.grid_search_id = grid_search_id
        self.target_pos = target_pos
        self.shuffle = shuffle
        self.re_eval = re_eval
        self.keep_interim_results = keep_interim_results

    def _get_fold_indices(self) -> List[List[int]]:
        splitter = SplitterFactory.get_cv_splitter(num_folds=self.num_folds,
                                                   stratification=self.stratification,
                                                   target_pos=self.target_pos,
                                                   shuffle=self.shuffle,
                                                   seed=self.seed)
        indices = splitter.get_indices(dataset_iterator=self.dataset_iterator)
        return indices

    @staticmethod
    def _create_folds_splits(folds_indices: List[List[int]]) -> List[Dict[str, Any]]:
        # folds
        # [fold_1_indices, fold_2_indices ...]
        splits = []
        for val_fold_id, val_fold_indices in enumerate(folds_indices):
            # create train fold
            train_fold_indices = []
            for i, fold in enumerate(folds_indices):
                if i != val_fold_id:
                    train_fold_indices = train_fold_indices + fold

            split = {
                "id_val_fold_id": val_fold_id,
                "id_split_indices": {
                    "train": train_fold_indices,
                    "val": val_fold_indices
                }
            }
            splits.append(split)
        return splits

    def create_blue_prints(self, blue_print_type: Type[BluePrint], job_type: AbstractGymJob.Type, gs_config: Dict[str, Any], num_epochs: int,
                           dashify_logging_path: str) -> List[Type[BluePrint]]:

        run_id_to_config_dict = {run_id: config for run_id, config in enumerate(GridSearch.create_gs_from_config_dict(gs_config))}

        fold_indices = self._get_fold_indices()

        splits: List[Dict[str, Any]] = CrossValidation._create_folds_splits(fold_indices)

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
                                      run_mode=AbstractGymJob.Mode.TRAIN if not self.re_eval else AbstractGymJob.Mode.EVAL,
                                      job_type=job_type,
                                      experiment_config=experiment_config_injected,
                                      dashify_logging_path=dashify_logging_path,
                                      num_epochs=num_epochs,
                                      grid_search_id=self.grid_search_id,
                                      experiment_id=experiment_id)
                blueprints.append(bp)
                experiment_id = experiment_id + 1
        return blueprints

    def run(self, blue_print_type: Type[BluePrint], gym: Gym, gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        job_type = AbstractGymJob.Type.STANDARD if self.keep_interim_results else AbstractGymJob.Type.LITE
        blueprints = self.create_blue_prints(blue_print_type=blue_print_type,
                                             gs_config=gs_config,
                                             dashify_logging_path=dashify_logging_path,
                                             num_epochs=num_epochs,
                                             job_type=job_type)
        gym.add_blue_prints(blueprints)
        gym.run(parallel=True)
