import random

import numpy as np
from data_stack.dataset.iterator import SequenceDatasetIterator
import torch


class MockedIterator(SequenceDatasetIterator):

    def __init__(self, num_samples: int = 500, seed=0):
        random.seed(seed)
        targets = [4, 3, 2, 1, 0] * int(num_samples / 5)
        samples = [[0, 1, 2, 3, 4]] * num_samples
        targets = torch.from_numpy(np.array(targets))
        samples = torch.from_numpy(np.array(samples))
        dataset_sequences = [samples, targets, targets]
        super().__init__(dataset_sequences=dataset_sequences)
