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

    def test_split_data_loaders(self, iterator_train: InformedDatasetIteratorIF):
        torch.manual_seed(0)
        iterator_dict = {"random_split": iterator_train, "weighted_random_split": iterator_train, "in_order_split": iterator_train}
        sampling_strategies = {"random_split": {"strategy": "RANDOM", "seed": 10},
                               "weighted_random_split": {"strategy": "WEIGHTED_RANDOM", "seed": 15, "label_pos": 0},
                               "in_order_split": {"strategy": "IN_ORDER", "seed": 10}
                               }
        splitted_data_loaders = DatasetLoaderFactory.get_splitted_data_loaders(dataset_splits=iterator_dict,
                                                                               batch_size=1,
                                                                               collate_fn=None,
                                                                               sampling_strategies=sampling_strategies)
        
        # iterate through all dataloaders 
        random_samples = [int(i[0]) for i in splitted_data_loaders["random_split"]]
        weighted_samples = [int(i[0]) for i in splitted_data_loaders["weighted_random_split"]]
        in_order_samples = [int(i[0]) for i in splitted_data_loaders["in_order_split"]]

        # make sure the number of samples matches the iterator length
        assert len(random_samples) == len(iterator_train)
        assert len(weighted_samples) == len(iterator_train)
        assert len(in_order_samples) == len(iterator_train)

        iterator_samples = [i[0] for i in iterator_train]
        # make sure the in_order split is actually in order
        assert in_order_samples == iterator_samples
        # make sure that random sampler is not in order
        assert random_samples != iterator_samples
        # only the order should be different but not the number of samples (we don't resample, we just shuffle the order)
        assert Counter(random_samples) == {2: 200, 3: 300, 1: 100}
        # make sure that the each class has the same probability of being drawn
        assert Counter(weighted_samples) == {3: 212, 2: 201, 1: 187}
        

