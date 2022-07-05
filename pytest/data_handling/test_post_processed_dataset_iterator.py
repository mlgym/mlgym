import pytest
from data_stack.dataset.iterator import InformedDatasetIterator
from data_stack.dataset.meta import IteratorMeta, DatasetMeta
from ml_gym.data_handling.iterators import PostProcessedDatasetIterator
from ml_gym.data_handling.postprocessors.postprocessor import OneHotEncodedTargetPostProcessor

from postprocessors.mocked_class import MockedIterator


class TestPostProcessedDatasetIterator:
    @pytest.fixture
    def iterator(self):
        iterator = MockedIterator()
        iterator_meta = IteratorMeta(sample_pos=0, target_pos=1, tag_pos=2)
        dataset_meta = DatasetMeta(identifier="identifier", dataset_name="dataset_name",
                                   dataset_tag="dataset_tag", iterator_meta=iterator_meta)
        iterator = InformedDatasetIterator(iterator, dataset_meta)
        return iterator

    @pytest.fixture
    def post_processor(self):
        postprocessor = OneHotEncodedTargetPostProcessor(target_vector_size=10, target_position=1)
        return postprocessor

    def test_len(self, iterator, post_processor):
        postprocess_dataset_iterator = PostProcessedDatasetIterator(dataset_iterator=iterator,
                                                                    post_processor=post_processor)
        assert len(postprocess_dataset_iterator) == len(iterator)
        assert postprocess_dataset_iterator.underlying_iterators[0] == iterator
        item = postprocess_dataset_iterator[1]
        assert int(item[1][6].numpy()) == 1
