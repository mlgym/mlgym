from torch.utils.data import DataLoader
from torch.utils.data.sampler import WeightedRandomSampler
from typing import Callable, Dict
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from torch.utils.data.sampler import Sampler
from collections import Counter


class DatasetLoaderFactory:
    @staticmethod
    def get_splitted_data_loaders(dataset_splits: Dict[str, InformedDatasetIteratorIF], batch_size: int, collate_fn: Callable = None,
                                  weigthed_sampling_split_name: str = None, label_pos: int = 2) -> Dict[str, "DatasetLoader"]:
        # NOTE: Weighting is only applied to the split specified by `weigthed_sampling_split_name`.
        data_loaders = {split_name: DatasetLoader(dataset_iterator=dataset_split,
                                                  batch_size=batch_size,
                                                  sampler=SamplerFactory.get_weighted_sampler(
                                                      dataset_split, label_pos) if split_name == weigthed_sampling_split_name else None,
                                                  collate_fn=collate_fn) for split_name, dataset_split in dataset_splits.items()}
        return data_loaders


class SamplerFactory:

    @staticmethod
    def get_weighted_sampler(dataset: InformedDatasetIteratorIF, label_pos: int = 2):
        """Returns a WeightedRandomSampler by counting the tags (sic!) over all samples.
        Note, we don't count over targets as they might e.g., be one hot encoded.

        Args:
            dataset (InformedDatasetIteratorIF): Iterator to calculate the sampler from

        Returns:
            [WeightedRandomSampler]: Instance of WeightedRandomSampler.
        """
        # get the class weights
        target_counts = Counter([int(sample[label_pos]) for sample in dataset])  # uses generator expression
        target_tuples = [(k, v) for k, v in sorted(target_counts.items(), key=lambda item: item[0])]
        class_weights = {target_key: 1./target_count for target_key, target_count in target_tuples}
        sample_weights = [class_weights[sample[label_pos]] for sample in dataset]
        sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(dataset))
        return sampler


class DatasetLoader(DataLoader):
    def __init__(self, dataset_iterator: InformedDatasetIteratorIF, batch_size: int, sampler: Sampler, collate_fn: Callable = None):
        super().__init__(dataset=dataset_iterator, sampler=sampler, batch_size=batch_size, collate_fn=collate_fn)

    @property
    def dataset_name(self) -> str:
        return self.dataset.dataset_meta.dataset_name
