import pytest
from data_stack.dataset.iterator import InformedDatasetIteratorIF, SequenceDatasetIterator
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.meta import MetaFactory
from ml_gym.data_handling.dataset_loader import SamplerFactory, DatasetLoaderFactory
import torch
from collections import Counter


class TestSamplerFactory:

    @pytest.fixture
    def iterator_train(self) -> str:
        sequence = [1]*100 + [2]*200 + [3]*300
        iterator = SequenceDatasetIterator([sequence])
        iterator_meta = MetaFactory.get_iterator_meta(sample_pos=0, target_pos=0, tag_pos=0)
        meta = MetaFactory.get_dataset_meta(identifier="test dataset id",
                                            dataset_name="test_dataset",
                                            dataset_tag="train",
                                            iterator_meta=iterator_meta)
        return InformedDatasetFactory.get_dataset_iterator(iterator, meta)

    @pytest.fixture
    def iterator_test(self) -> str:
        sequence = [3]*30 + [1]*10 + [2]*20
        iterator = SequenceDatasetIterator([sequence])
        iterator_meta = MetaFactory.get_iterator_meta(sample_pos=0, target_pos=0, tag_pos=0)
        meta = MetaFactory.get_dataset_meta(identifier="test dataset id",
                                            dataset_name="test_dataset",
                                            dataset_tag="train",
                                            iterator_meta=iterator_meta)
        return InformedDatasetFactory.get_dataset_iterator(iterator, meta)

    def test_weighted_random_sampler(self, iterator_train: InformedDatasetIteratorIF):
        sampler = SamplerFactory.get_weighted_sampler(iterator_train, label_pos=0)
        sample_weights = sampler.weights
        assert all(sample_weights[0: 100] == sample_weights[0])
        assert all(sample_weights[100: 300] == sample_weights[100])
        assert all(sample_weights[300: 600] == sample_weights[300])
        assert sample_weights[0] * 100 == 1
        assert sample_weights[100] * 200 == 1
        assert sample_weights[300] * 300 == 1

    def test_split_data_loaders(self, iterator_train: InformedDatasetIteratorIF, iterator_test: InformedDatasetIteratorIF):
        torch.manual_seed(0)
        iterator_dict = {"train": iterator_train, "test": iterator_test}
        splitted_data_loaders = DatasetLoaderFactory.get_splitted_data_loaders(
            iterator_dict, batch_size=1, collate_fn=None, weigthed_sampling_split_name="train", label_pos=0)
        train_samples = [int(i[0]) for i in splitted_data_loaders["train"]]
        test_samples = [int(i[0]) for i in splitted_data_loaders["test"]]
        assert len(train_samples) == len(iterator_train)
        assert len(test_samples) == len(iterator_test)
        assert Counter(train_samples) == {2: 218, 3: 192, 1: 190}
        assert Counter(test_samples) == {2: 20, 3: 30, 1: 10}
