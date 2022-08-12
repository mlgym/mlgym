from ml_gym.validation.nested_cross_validation import NestedCV
from data_stack.dataset.iterator import DatasetIteratorIF, SequenceDatasetIterator
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.meta import MetaFactory
import torch
import pytest
from collections import Counter

from pytests.test_env.fixtures import LoggingFixture, DeviceFixture
from pytests.test_env.validation_fixtures import ValidationFixtures


class TestNestedCV(LoggingFixture, DeviceFixture, ValidationFixtures):

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

    def test__get_fold_indices_stratified(self, iterator: DatasetIteratorIF):
        nested_cv = NestedCV(dataset_iterator=iterator,
                             num_outer_loop_folds=5,
                             num_inner_loop_folds=2,
                             inner_stratification=True,
                             outer_stratification=True,
                             target_pos=1,
                             shuffle=False,
                             grid_search_id=0,
                             seed=1)
        outer_folds_indices, inner_folds_indices = nested_cv._get_fold_indices()

        # check stratification
        for outer_fold in outer_folds_indices:
            target_counts = dict(Counter([iterator[i][1].item() for i in outer_fold]))
            assert target_counts == {1.0: 20, 2.0: 40, 3.0: 60}

        for outer_fold in inner_folds_indices:
            for inner_fold in outer_fold:
                target_counts = dict(Counter([iterator[i][1].item() for i in inner_fold]))
                assert target_counts == {1.0: 40, 2.0: 80, 3.0: 120}

        # check that there is no intersection between outer folds
        for i, outer_fold_1 in enumerate(outer_folds_indices):
            for j, outer_fold_2 in enumerate(outer_folds_indices):
                if i != j:
                    assert set(outer_fold_1).isdisjoint(outer_fold_2)

        # check that there is not intersection between inner folds
        for outer_fold in inner_folds_indices:
            for i, inner_fold_1 in enumerate(outer_fold):
                for j, inner_fold_2 in enumerate(outer_fold):
                    if i != j:
                        assert set(inner_fold_1).isdisjoint(inner_fold_2)

        # check that every indice in an inner fold is existing in the outer fold and vice versa
        for outer_fold_id, outer_fold in enumerate(outer_folds_indices):
            assert len(outer_fold) * 4 == sum([len(fold) for fold in inner_folds_indices[outer_fold_id]])
            assert set(outer_fold).isdisjoint(set([i for fold in inner_folds_indices[outer_fold_id] for i in fold]))

    def test__create_outer_folds_splits(self, iterator: DatasetIteratorIF):
        nested_cv = NestedCV(dataset_iterator=iterator,
                             num_outer_loop_folds=5,
                             num_inner_loop_folds=2,
                             inner_stratification=True,
                             outer_stratification=True,
                             target_pos=1,
                             shuffle=False,
                             grid_search_id=0,
                             seed=1)
        outer_folds_indices, _ = nested_cv._get_fold_indices()
        splits = NestedCV._create_outer_folds_splits(outer_folds_indices)
        for split in splits:
            assert len(split["id_split_indices"]["train"]) == len(split["id_split_indices"]["test"]) * 4
            assert len(split["id_split_indices"]["train"]) == len(set(split["id_split_indices"]["train"]))
            assert len(split["id_split_indices"]["test"]) == len(set(split["id_split_indices"]["test"]))
            assert set(split["id_split_indices"]["test"]).isdisjoint(set(split["id_split_indices"]["train"]))

    def test__create_inner_folds_splits(self, iterator: DatasetIteratorIF):
        num_inner_loop_folds = 2
        nested_cv = NestedCV(dataset_iterator=iterator,
                             num_outer_loop_folds=5,
                             num_inner_loop_folds=num_inner_loop_folds,
                             inner_stratification=True,
                             outer_stratification=True,
                             target_pos=1,
                             shuffle=False,
                             grid_search_id=0,
                             seed=1)
        outer_folds_indices, inner_folds_indices = nested_cv._get_fold_indices()
        outer_splits = NestedCV._create_outer_folds_splits(outer_folds_indices)
        inner_splits = NestedCV._create_inner_folds_splits(inner_folds_indices)
        for inner_split in inner_splits:
            assert len(inner_split["id_split_indices"]["train"]) == len(inner_split["id_split_indices"]["test"]) * (
                    num_inner_loop_folds - 1)
            assert len(inner_split["id_split_indices"]["train"]) == len(set(inner_split["id_split_indices"]["train"]))
            assert len(inner_split["id_split_indices"]["test"]) == len(set(inner_split["id_split_indices"]["test"]))
            assert set(inner_split["id_split_indices"]["test"]).isdisjoint(
                set(inner_split["id_split_indices"]["train"]))
            outer_split = outer_splits[inner_split["id_outer_test_fold_id"]]
            outer_split_indices = outer_split["id_split_indices"]["train"]
            assert len(outer_split_indices) == len(inner_split["id_split_indices"]["train"]) + len(
                inner_split["id_split_indices"]["test"])
