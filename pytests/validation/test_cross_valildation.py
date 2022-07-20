import os.path
from collections import Counter
from multiprocessing import Queue
from typing import Type, Dict, Any, List

import numpy as np
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.util.grid_search import GridSearch
from ml_gym.util.logger import QueuedLogging
from ml_gym.validation.cross_validation import CrossValidation
from data_stack.dataset.iterator import SequenceDatasetIterator
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.meta import MetaFactory
import torch

from pytests.test_env.fixtures import LoggingFixture
from pytests.test_env.mocked_blueprint import ConvNetBluePrint
import pytest


class TestCrossValidation(LoggingFixture):
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
        return os.path.join(os.path.abspath('.'), "..", "..", "example", "grid_search/gs_config.yml")

        # return "example/grid_search/gs_config.yml"

    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def gs_config(self, gs_path) -> Dict[str, Any]:
        gs_config = YAMLConfigLoader.load(gs_path)
        return gs_config

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
    def device_ids(self) -> List[int]:
        return [0, 1, 2, 3]

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    @pytest.fixture
    def cv(self, iterator, num_folds) -> CrossValidation:
        cv = CrossValidation(dataset_iterator=iterator,
                             num_folds=num_folds,
                             stratification=False,
                             target_pos=1,
                             shuffle=True,
                             grid_search_id=0,
                             seed=1)

        return cv

    def test_get_fold_indices(self, iterator, cv):
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

    def test_create_folds_splits(self, iterator, cv):
        indices = cv._get_fold_indices()
        splits = cv._create_folds_splits(indices)
        for split in splits:
            assert len(split["id_split_indices"]["train"]) == len(split["id_split_indices"]["val"]) * 4
            assert len(split["id_split_indices"]["train"]) == len(set(split["id_split_indices"]["train"]))
            assert len(split["id_split_indices"]["val"]) == len(set(split["id_split_indices"]["val"]))
            assert set(split["id_split_indices"]["val"]).isdisjoint(set(split["id_split_indices"]["train"]))

    @pytest.mark.parametrize("job_type",
                             [AbstractGymJob.Type.STANDARD, AbstractGymJob.Type.LITE])
    def test_create_blue_prints(self, iterator, cv, blue_print_type: Type[BluePrint], job_type: AbstractGymJob.Type,
                                gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str):
        blueprints = cv.create_blue_prints(blue_print_type=blue_print_type,
                                           gs_config=gs_config,
                                           dashify_logging_path=dashify_logging_path,
                                           num_epochs=num_epochs,
                                           job_type=job_type)
        gs_config = GridSearch.create_gs_from_config_dict(gs_config)
        assert len(blueprints) == len(gs_config) * len(cv._get_fold_indices())

    # @pytest.mark.parametrize("job_type",
    #                          [AbstractGymJob.Type.STANDARD])
    # def test_run(self, iterator, cv, blue_print_type: Type[BluePrint], job_type: AbstractGymJob.Type,
    #              gs_config: Dict[str, Any], num_epochs: int, dashify_logging_path: str, process_count: int,
    #              device_ids: List[int], log_std_to_file: bool, log_dir_path: str, start_logging):
    #     blueprints = cv.create_blue_prints(blue_print_type=blue_print_type,
    #                                        gs_config=gs_config,
    #                                        dashify_logging_path=dashify_logging_path,
    #                                        num_epochs=num_epochs,
    #                                        job_type=job_type)
    #     gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
    #     gym.add_blue_prints(blueprints)
    #     gym.run(parallel=True)
    #     QueuedLogging.stop_listener()
