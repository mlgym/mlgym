import pytest
from ml_gym.blueprints.constructables import DatasetIteratorConstructable, Requirement, \
    DatasetIteratorSplitsConstructable, \
    CombinedDatasetIteratorConstructable, FilteredLabelsIteratorConstructable, MappedLabelsIteratorConstructable, \
    FeatureEncodedIteratorConstructable, IteratorViewConstructable, InMemoryDatasetIteratorConstructable, \
    ShuffledDatasetIteratorConstructable, OneHotEncodedTargetsIteratorConstructable
import tempfile
import shutil
from data_stack.repository.repository import DatasetRepository
from typing import Dict
from data_stack.dataset.iterator import InformedDatasetIteratorIF, InformedDatasetIterator, InMemoryDatasetIterator, \
    DatasetIteratorView
from ml_gym.data_handling.iterators import PostProcessedDatasetIterator

from mocked_classes import MockedMNISTFactory


class IteratorFixtures:
    @pytest.fixture
    def tmp_folder_path(self) -> str:
        path = tempfile.mkdtemp()
        yield path
        shutil.rmtree(path)

    @pytest.fixture
    def repository(self):
        dataset_repository: DatasetRepository = DatasetRepository()
        dataset_repository.register("mnist", MockedMNISTFactory())
        return dataset_repository

    @pytest.fixture
    def repository_requirement(self, repository) -> Dict[str, Requirement]:
        return {"repository": Requirement(components=repository)}

    @pytest.fixture
    def informed_iterators(self, repository_requirement):
        constructable = DatasetIteratorConstructable(component_identifier="iterator_component",
                                                     requirements=repository_requirement,
                                                     dataset_identifier="mnist",
                                                     split_configs=[{"split": "train"}, {"split": "test"}])
        iterators = constructable.construct()
        return iterators


class TestDatasetIteratorSplitsConstructable(IteratorFixtures):

    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train"])}
        split_configs = {"train": {"train_1": 0.7, "train_2": 0.3}}
        constructable = DatasetIteratorSplitsConstructable(component_identifier="splitted_component",
                                                           requirements=requirements,
                                                           split_configs=split_configs)
        splitted_iterators = constructable.construct()
        iterator_1, iterator_2 = splitted_iterators["train_1"], splitted_iterators["train_2"]
        sample, target, tag = iterator_1[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)
        assert isinstance(iterator_1, InformedDatasetIteratorIF)
        assert isinstance(iterator_2, InformedDatasetIteratorIF)
        assert int(len(informed_iterators["train"]) * 0.7) == len(iterator_1)
        assert int(len(informed_iterators["train"]) * 0.3) == len(iterator_2)
        # print(DatasetIteratorReportGenerator.generate_report(iterator_1))


class TestCombinedDatasetIteratorConstructable(IteratorFixtures):

    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        combine_configs = [
            {"new_split": "full", "old_splits": [{"iterators_name": "iterators", "splits": ["train", "test"]}]},
            {"new_split": "train", "old_splits": [{"iterators_name": "iterators", "splits": ["train"]}]},
            {"new_split": "test", "old_splits": [{"iterators_name": "iterators", "splits": ["test"]}]}]
        constructable = CombinedDatasetIteratorConstructable(component_identifier="combined_component",
                                                             requirements=requirements,
                                                             combine_configs=combine_configs)
        iterators = constructable.construct()
        iterator_full, iterator_train, iterator_test = iterators["full"], iterators["train"], iterators["test"]
        sample, target, tag = iterator_full[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(iterator_full, InformedDatasetIteratorIF)
        assert isinstance(iterator_train, InformedDatasetIteratorIF)
        assert isinstance(iterator_test, InformedDatasetIteratorIF)

        assert int(len(iterator_full)) == len(iterator_train) + len(iterator_test)
        # print(DatasetIteratorReportGenerator.generate_report(iterator_full))


class TestInMemoryDatasetIteratorConstructable(IteratorFixtures):
    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        constructable = InMemoryDatasetIteratorConstructable(component_identifier="memory_component",
                                                             requirements=requirements)
        iterators = constructable.construct()
        iterator_train, iterator_test = iterators["train"], iterators["test"]
        sample, target, tag = iterator_train[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(iterator_train._dataset_iterator, InMemoryDatasetIterator)
        assert isinstance(iterator_test._dataset_iterator, InMemoryDatasetIterator)


class TestShuffledDatasetIteratorConstructable(IteratorFixtures):
    def test_constructable(self, informed_iterators):
        applicable_splits = ["train", "test"]
        seeds = {"train": 0, "test": 0}
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}

        sample, target, tag = informed_iterators["train"][0]

        # construct a ShuffledDatasetIterator
        shuffled_constructable = ShuffledDatasetIteratorConstructable(component_identifier="shuffled_component",
                                                                      requirements=requirements,
                                                                      applicable_splits=applicable_splits,
                                                                      seeds=seeds)

        shuffled_iterators = shuffled_constructable.construct()

        shuffled_sample, shuffled_target, shuffled_tag = shuffled_iterators["train"][0]

        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(shuffled_iterators["train"]._dataset_iterator, DatasetIteratorView)
        assert isinstance(shuffled_iterators["test"]._dataset_iterator, DatasetIteratorView)


class TestFilteredLabelsIteratorConstructable(IteratorFixtures):

    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}

        filtered_labels = [1, 3, 5]
        constructable = FilteredLabelsIteratorConstructable(component_identifier="filtered_component",
                                                            requirements=requirements,
                                                            filtered_labels=filtered_labels,
                                                            applicable_splits=["train"])
        iterators = constructable.construct()
        iterator_train_filtered, iterator_test_not_filtered = iterators["train"], iterators["test"]
        sample, target, tag = iterator_train_filtered[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(iterator_train_filtered, InformedDatasetIteratorIF)
        assert isinstance(iterator_test_not_filtered, InformedDatasetIteratorIF)
        assert all([t in filtered_labels for _, _, t in iterator_train_filtered])
        assert any([t not in filtered_labels for _, _, t in iterator_test_not_filtered])
        assert any([t not in filtered_labels for _, _, t in informed_iterators["train"]])
        assert any([t not in filtered_labels for _, _, t in informed_iterators["test"]])
        # print(DatasetIteratorReportGenerator.generate_report(iterator_train_filtered))


class TestMappedLabelsIteratorConstructable(IteratorFixtures):

    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}

        mappings = [{"previous_labels": [1, 2, 3, 4], "new_label": 0}]
        constructable = MappedLabelsIteratorConstructable(component_identifier="mapped_component",
                                                          requirements=requirements,
                                                          mappings=mappings,
                                                          applicable_splits=["train"])
        iterators = constructable.construct()
        iterator_train_mapped, iterator_test_not_mapped = iterators["train"], iterators["test"]
        sample, target, tag = iterator_train_mapped[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(iterator_train_mapped, InformedDatasetIteratorIF)
        assert isinstance(iterator_test_not_mapped, InformedDatasetIteratorIF)
        assert all([t not in mappings[0]["previous_labels"] for _, _, t in iterator_train_mapped])
        assert any([t in mappings[0]["previous_labels"] for _, _, t in iterator_test_not_mapped])
        assert any([t in mappings[0]["previous_labels"] for _, _, t in informed_iterators["train"]])
        assert any([t in mappings[0]["previous_labels"] for _, _, t in informed_iterators["test"]])
        # print(DatasetIteratorReportGenerator.generate_report(iterator_train_mapped))


class TestFeatureEncodedIteratorConstructable(IteratorFixtures):

    # NOTE, this test does not actually encode. It just makes sure that the factories are called appropiately.
    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}

        feature_encoding_configs = []
        constructable = FeatureEncodedIteratorConstructable(component_identifier="feature_encoding_component",
                                                            requirements=requirements,
                                                            feature_encoding_configs=feature_encoding_configs,
                                                            applicable_splits=["train"])
        iterators = constructable.construct()
        iterator_train_encoded = iterators["train"]
        sample, target, tag = iterator_train_encoded[0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)

        assert isinstance(iterator_train_encoded._dataset_iterator, PostProcessedDatasetIterator)
        # print(DatasetIteratorReportGenerator.generate_report(iterator_train_encoded))


class TestOneHotEncodedTargetsIteratorConstructable(IteratorFixtures):
    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        target_vector_size = 10
        constructable = OneHotEncodedTargetsIteratorConstructable(component_identifier="one_hot_targets_component",
                                                                  requirements=requirements,
                                                                  target_vector_size=target_vector_size,
                                                                  applicable_splits=["train"])
        iterators = constructable.construct()
        _, label, _ = informed_iterators["train"][0]
        iterator_train_encoded = iterators["train"]
        sample, target, tag = iterator_train_encoded[0]
        assert list(sample.shape) == [28, 28]
        assert len(target) == target_vector_size
        assert target[int(label)] == 1

        assert isinstance(iterator_train_encoded._dataset_iterator, PostProcessedDatasetIterator)


class TestIteratorViewConstructable(IteratorFixtures):

    def test_constructable(self, informed_iterators):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        num_indices_train = 15
        num_indices_test = 10
        constructable = IteratorViewConstructable(component_identifier="mapped_component",
                                                  requirements=requirements,
                                                  split_indices={"train": list(range(num_indices_train)),
                                                                 "test": list(range(num_indices_test))},
                                                  applicable_split="train")
        iterator_views = constructable.construct()
        iterator_view_train, iterator_view_test = iterator_views["train"], iterator_views["test"]
        assert isinstance(iterator_view_train, InformedDatasetIteratorIF)
        assert isinstance(iterator_view_test, InformedDatasetIteratorIF)
        assert len(iterator_view_train) == num_indices_train
        assert len(iterator_view_test) == num_indices_test
        try:
            iterator_view_train[num_indices_train]
            assert False
        except:
            assert True
        # print(DatasetIteratorReportGenerator.generate_report(iterator_view_train))
