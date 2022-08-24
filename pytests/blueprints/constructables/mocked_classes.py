from data_stack.dataset.iterator import DatasetIteratorIF
from data_stack.dataset.iterator import SequenceDatasetIterator
from data_stack.dataset.factory import BaseDatasetFactory
import torch
import random
from data_stack.dataset.meta import IteratorMeta
from typing import Tuple, Dict, Any, List

from ml_gym.data_handling.postprocessors.collator import Collator
from ml_gym.models.nn.net import NNModel


class MockedMNISTIterator(SequenceDatasetIterator):

    def __init__(self, num_samples: int = 500):
        targets = [random.randint(0, 9) for _ in range(num_samples)]
        samples = torch.rand(num_samples, 28, 28)
        dataset_sequences = [samples, targets, targets]
        super().__init__(dataset_sequences=dataset_sequences)


class MockedMNISTFactory(BaseDatasetFactory):
    def __init__(self):
        super().__init__(storage_connector=None)

    def get_dataset_iterator(self, config: Dict[str, Any] = None) -> Tuple[DatasetIteratorIF, IteratorMeta]:
        return MockedMNISTIterator(), IteratorMeta(sample_pos=0, target_pos=1, tag_pos=2)


class MockedCollator(Collator):
    target_publication_key: str = None

    def __call__(self, batch: List[torch.Tensor]):
        pass


class MockedNNModel(NNModel):
    def __init__(self, seed, layer_config: Dict = None, prediction_publication_key: str = None):
        super().__init__(seed=seed)
        self.prediction_publication_key = prediction_publication_key

    def forward_impl(self, inputs: torch.Tensor):
        pass


