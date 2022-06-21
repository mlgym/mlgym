import random

from data_stack.dataset.iterator import SequenceDatasetIterator
import torch


class MockedIterator(SequenceDatasetIterator):

    def __init__(self, num_samples: int = 500):
        targets = [random.randint(0, 9) for _ in range(num_samples)]
        samples = torch.randint(10, (num_samples, 50))
        dataset_sequences = [samples, targets, targets]
        super().__init__(dataset_sequences=dataset_sequences)
