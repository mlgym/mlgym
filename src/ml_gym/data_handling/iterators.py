from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.data_handling.postprocessors.postprocessor import PostProcessorIf
from typing import List


class PostProcessedDatasetIterator(DatasetIteratorIF):

    def __init__(self, dataset_iterator: DatasetIteratorIF, post_processor: PostProcessorIf):
        self._dataset_iterator = dataset_iterator
        self._post_processor = post_processor

    def __len__(self):
        return len(self._dataset_iterator)

    def __getitem__(self, index: int):
        return self._post_processor.postprocess(self._dataset_iterator[index])

    @property
    def underlying_iterators(self) -> List[DatasetIteratorIF]:
        return [self._dataset_iterator]
