from typing import Dict, Any, List, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.blueprints.blue_prints import BluePrint
from data_stack.dataset.splitter import SplitterFactory
from ml_gym.modes import RunMode
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable
from ml_gym.validation.validator import ValidatorIF
from ml_gym.blueprints.component_factory import Injector
from ml_gym.util.grid_search import GridSearch
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF


class CrossValidation(ValidatorIF):
    def __init__(self, dataset_iterator: DatasetIteratorIF, num_folds: int, stratification: bool,
                 target_pos: int, shuffle: bool, seed: int, run_mode: RunMode):
        self.num_folds = num_folds
        self.stratification = stratification
        self.dataset_iterator = dataset_iterator
        self.seed = seed
        self.target_pos = target_pos
        self.shuffle = shuffle
        self.run_mode = run_mode

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

    def create_blue_prints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any], num_epochs: int,
                           gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                           logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> List[Type[BluePrint]]:

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
                bp = BluePrint.create_blueprint(blue_print_class=blue_print_type,
                                                run_mode=self.run_mode,
                                                experiment_config=experiment_config_injected,
                                                num_epochs=num_epochs,
                                                grid_search_id=grid_search_id,
                                                experiment_id=experiment_id,
                                                logger_collection_constructable=logger_collection_constructable,
                                                gs_api_client_constructable=gs_api_client_constructable)
                blueprints.append(bp)
                experiment_id = experiment_id + 1
        return blueprints

    def create_blueprints(self, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any], num_epochs: int,
                          gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                          logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> List[BluePrint]:
        blueprints = self.create_blue_prints(blue_print_type=blue_print_type,
                                             gs_config=gs_config,
                                             num_epochs=num_epochs,
                                             logger_collection_constructable=logger_collection_constructable,
                                             gs_api_client_constructable=gs_api_client_constructable)
        return blueprints
