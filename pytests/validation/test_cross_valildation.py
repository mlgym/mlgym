import os.path
from collections import Counter
from typing import Type, Dict, Any, List
from datetime import datetime

import numpy as np
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.util.grid_search import GridSearch
from ml_gym.util.logger import QueuedLogging
from ml_gym.validation.cross_validation import CrossValidation
from data_stack.dataset.iterator import SequenceDatasetIterator, InformedDatasetIterator
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.meta import MetaFactory
import torch
from ml_gym.validation.validator_factory import ValidatorFactory

from pytests.test_env.fixtures import LoggingFixture, DeviceFixture
from pytests.test_env.mocked_blueprint import ConvNetBluePrint
import pytest


class TestCrossValidation(LoggingFixture, DeviceFixture):
    @pytest.fixture
    def iterator(self) -> str:
        targets = [1] * 100 + [2] * 200 + [3] * 300
        sequence_targets = torch.Tensor(targets)
        sequence_samples = torch.ones_like(sequence_targets)

        iterator = SequenceDatasetIterator([sequence_samples, sequence_targets])
        iterator_meta = MetaFactory.get_iterator_meta(sample_pos=0, target_pos=1, tag_pos=1)
        meta = MetaFactory.get_dataset_meta(identifier="dataset id",
                                            dataset_name="dataset",
                                            dataset_tag="full",
                                            iterator_meta=iterator_meta)
        return InformedDatasetFactory.get_dataset_iterator(iterator, meta)

    @pytest.fixture
    def gs_path(self) -> str:
        return os.path.join(os.path.abspath('.'), "..", "test_env", "cross_validation/gs_config_cv.yml")
        # return "example/grid_search/gs_config.yml"

    @pytest.fixture
    def cv_path(self) -> str:
        return os.path.join(os.path.abspath('.'), "..", "test_env", "cross_validation/cv_config.yml")
        # return "example/grid_search/gs_config.yml"

    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def gs_config(self, gs_path) -> Dict[str, Any]:
        gs_config = YAMLConfigLoader.load(gs_path)
        return gs_config

    @pytest.fixture
    def cv_config(self, cv_path) -> Dict[str, Any]:
        cv_config = YAMLConfigLoader.load(cv_path)
        return cv_config

    @pytest.fixture
    def num_epochs(self) -> int:
        return 2

    @pytest.fixture
    def dashify_logging_path(self) -> str:
        return "dashify_logging"

    @pytest.fixture
    def blue_print_type(self) -> Type:
        return ConvNetBluePrint

    @pytest.fixture
    def num_folds(self) -> int:
        return 5

    @pytest.fixture
    def process_count(self) -> int:
        return 2

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    @pytest.fixture
    def cv(self, iterator: InformedDatasetIterator, num_folds: int) -> CrossValidation:
        cv = CrossValidation(dataset_iterator=iterator,
                             num_folds=num_folds,
                             stratification=False,
                             target_pos=1,
                             shuffle=True,
                             grid_search_id=datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
                             seed=1)

        return cv

    @pytest.fixture
    def keep_interim_results(self):
        return False

    def test_get_fold_indices(self, iterator: InformedDatasetIterator, cv: CrossValidation):
        indices = cv._get_fold_indices()

        # check that there is no intersection between folds
        for i, outer_fold_1 in enumerate(indices):
            for j, outer_fold_2 in enumerate(indices):
                if i != j:
                    assert set(outer_fold_1).isdisjoint(outer_fold_2)

        for folder_indices in indices:
            assert len(folder_indices) == 120
        # check each folds
        cat_indices = np.concatenate(indices, axis=0)
        target_counts = dict(Counter([iterator[i][1].item() for i in cat_indices]))
        assert target_counts == {1.0: 100, 2.0: 200, 3.0: 300}

    def test_create_folds_splits(self, cv: CrossValidation):
        indices = cv._get_fold_indices()
        splits = cv._create_folds_splits(indices)
        for split in splits:
            assert len(split["id_split_indices"]["train"]) == len(split["id_split_indices"]["val"]) * 4
            assert len(split["id_split_indices"]["train"]) == len(set(split["id_split_indices"]["train"]))
            assert len(split["id_split_indices"]["val"]) == len(set(split["id_split_indices"]["val"]))
            assert set(split["id_split_indices"]["val"]).isdisjoint(set(split["id_split_indices"]["train"]))

    @pytest.mark.parametrize("job_type", [AbstractGymJob.Type.STANDARD, AbstractGymJob.Type.LITE])
    def test_create_blue_prints(self, blue_print_type: Type[BluePrint],
                                job_type: AbstractGymJob.Type, gs_config: Dict[str, Any], cv_config: Dict[str, Any],
                                num_epochs: int,
                                dashify_logging_path: str,
                                keep_interim_results: bool):
        cross_validator = ValidatorFactory.get_cross_validator(gs_config=gs_config,
                                                               cv_config=cv_config,
                                                               grid_search_id=datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
                                                               blue_print_type=blue_print_type,
                                                               re_eval=False,
                                                               keep_interim_results=keep_interim_results)
        blueprints = cross_validator.create_blue_prints(blue_print_type=blue_print_type,
                                                        gs_config=gs_config,
                                                        dashify_logging_path=dashify_logging_path,
                                                        num_epochs=num_epochs,
                                                        job_type=job_type)
        gs_config = GridSearch.create_gs_from_config_dict(gs_config)
        assert len(blueprints) == len(gs_config) * len(cross_validator._get_fold_indices())
        for i, blueprint in enumerate(blueprints):
            blueprint.config['cv_experiment_information']["config"]['experiment_id'] = i
            blueprint.config['cv_experiment_information']["config"]['val_fold_id'] = i
            blueprint.job_type = AbstractGymJob.Type.STANDARD
            blueprint.run_id = str(i)
            blueprint.epochs = num_epochs

    @pytest.mark.parametrize("job_type", [AbstractGymJob.Type.STANDARD])
    def test_run(self, blue_print_type: Type[BluePrint], job_type: AbstractGymJob.Type,
                 gs_config: Dict[str, Any], cv_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str,
                 process_count: int, device_ids: List[int], log_std_to_file: bool, log_dir_path: str,
                 keep_interim_results: bool, start_logging):
        cross_validator = ValidatorFactory.get_cross_validator(gs_config=gs_config,
                                                               cv_config=cv_config,
                                                               grid_search_id=datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
                                                               blue_print_type=blue_print_type,
                                                               re_eval=False,
                                                               keep_interim_results=keep_interim_results)
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        cross_validator.run(blue_print_type, gym, gs_config, num_epochs, dashify_logging_path)
        QueuedLogging.stop_listener()
