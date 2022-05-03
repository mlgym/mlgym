from ml_gym.error_handling.exception import SamplerNotFoundError
from torch.utils.data import DataLoader
from torch.utils.data.sampler import RandomSampler, WeightedRandomSampler
from typing import Callable, Dict, Any
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from torch.utils.data.sampler import Sampler
from collections import Counter
import torch
from ml_gym.data_handling.postprocessors.collator import Collator
from enum import Enum


class DatasetLoaderFactory:

    @staticmethod
    def get_splitted_data_loaders_deprecated(dataset_splits: Dict[str, InformedDatasetIteratorIF], batch_size: int, collate_fn: Callable = None,
                                             weigthed_sampling_split_name: str = None, label_pos: int = 2, seeds: Dict[str, int] = None,
                                             drop_last: bool = False) -> Dict[str, "DatasetLoader"]:
        seeds = {} if seeds is None else seeds
        # NOTE: Weighting is only applied to the split specified by `weigthed_sampling_split_name`.
        data_loaders = {}
        for split_id, (split_name, dataset_split) in enumerate(dataset_splits.items()):
            seed = seeds[split_name] if split_name in seeds else None
            if split_name == weigthed_sampling_split_name:
                sampler = SamplerFactory.get_weighted_sampler(dataset_split, label_pos, seed)
            else:
                sampler = SamplerFactory.get_random_sampler(dataset_split, seed)

            data_loaders[split_name] = DatasetLoader(dataset_iterator=dataset_split,
                                                     batch_size=batch_size,
                                                     sampler=sampler,
                                                     collate_fn=collate_fn,
                                                     drop_last=drop_last)
        return data_loaders

    @staticmethod
    def get_splitted_data_loaders(dataset_splits: Dict[str, InformedDatasetIteratorIF], batch_size: int, collate_fn: Callable = None,
                                  drop_last: bool = False, sampling_strategies: Dict[str, Any] = None) -> Dict[str, "DatasetLoader"]:
        data_loaders = {}
        for split_id, (split_name, dataset_split) in enumerate(dataset_splits.items()):
            if split_name in sampling_strategies:
                config = sampling_strategies[split_name]
                strategy = SamplerFactory.SamplingStrategies[sampling_strategies[split_name]["strategy"]]
                config.pop("strategy")
                if strategy == SamplerFactory.SamplingStrategies.WEIGHTED_RANDOM:
                    sampler = SamplerFactory.get_weighted_sampler(dataset_split, **config)
                elif strategy == SamplerFactory.SamplingStrategies.RANDOM:
                    sampler = SamplerFactory.get_random_sampler(dataset_split, **config)
                elif strategy == SamplerFactory.SamplingStrategies.IN_ORDER:
                    sampler = None
                else:
                    raise SamplerNotFoundError(f"Could not find sampler with key {strategy}")
            else:
                sampler = None
            data_loaders[split_name] = DatasetLoader(dataset_iterator=dataset_split,
                                                     batch_size=batch_size,
                                                     sampler=sampler,
                                                     collate_fn=collate_fn,
                                                     drop_last=drop_last)
        return data_loaders


class SamplerFactory:

    class SamplingStrategies(Enum):
        RANDOM = "random"
        WEIGHTED_RANDOM = "weighted_random"
        IN_ORDER = "in_order"

    @staticmethod
    def get_weighted_sampler(dataset: InformedDatasetIteratorIF, label_pos: int = 2, seed: int = 0) -> Sampler:
        """Returns a WeightedRandomSampler by counting the tags (sic!) over all samples.
        Note, we don't count over targets as they might e.g., be one hot encoded.

        Args:
            dataset (InformedDatasetIteratorIF): Iterator to calculate the sampler from

        Returns:
            [WeightedRandomSampler]: Instance of WeightedRandomSampler.
        """
        rnd_generator = torch.Generator().manual_seed(seed) if seed is not None else None
        # get the class weights
        target_counts = Counter([int(sample[label_pos]) for sample in dataset])  # uses generator expression
        target_tuples = [(k, v) for k, v in sorted(target_counts.items(), key=lambda item: item[0])]
        class_weights = {target_key: 1./target_count for target_key, target_count in target_tuples}
        sample_weights = [class_weights[sample[label_pos]] for sample in dataset]
        sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(dataset), generator=rnd_generator)
        return sampler

    @staticmethod
    def get_random_sampler(dataset: InformedDatasetIteratorIF, seed: int = 0) -> Sampler:
        rnd_generator = torch.Generator().manual_seed(seed) if seed is not None else None
        return RandomSampler(data_source=dataset, generator=rnd_generator)


class DatasetLoader(DataLoader):
    def __init__(self, dataset_iterator: InformedDatasetIteratorIF, batch_size: int, sampler: Sampler,
                 collate_fn: Collator = None, drop_last: bool = False):
        super().__init__(dataset=dataset_iterator, sampler=sampler, batch_size=batch_size, collate_fn=collate_fn, drop_last=drop_last)

    @property
    def dataset_name(self) -> str:
        return self.dataset.dataset_meta.dataset_name

    @property
    def device(self) -> torch.device:
        return self.collate_fn.device

    @device.setter
    def device(self, d: torch.device):
        if self.collate_fn is not None:
            self.collate_fn.device = d
