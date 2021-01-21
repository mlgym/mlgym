from typing import Tuple, Any, Dict, List
from abc import ABC, abstractmethod
from data_stack.dataset.iterator import DatasetIteratorIF
from ml_gym.data_handling.postprocessors.feature_encoder import CategoricalEncoder, ContinuousEncoder, Encoder
import torch
import numpy as np
import tqdm


class PostProcessorIf(ABC):

    @abstractmethod
    def postprocess(self, sample: Tuple[Any]) -> Tuple[Any]:
        raise NotImplementedError


class FittablePostProcessorIf(PostProcessorIf):

    @abstractmethod
    def fit(self, iterator: DatasetIteratorIF):
        raise NotImplementedError


class LabelMapperPostProcessor(PostProcessorIf):

    class Mapping:
        def __init__(self, previous_labels: List[Any], new_label: Any):
            self.previous_labels: List[Any] = previous_labels
            self.new_label: Any = new_label

        def __contains__(self, label: Any):
            return label in self.previous_labels

    def __init__(self, mappings: List[Dict], target_position: int = 1, tag_position: int = 2):
        self.target_position = target_position
        self.tag_position = tag_position
        self.mappings: List[LabelMapperPostProcessor.Mapping] = [LabelMapperPostProcessor.Mapping(**mapping) for mapping in mappings]

    def postprocess(self, sample: Tuple[Any]) -> Tuple[Any]:
        for mapping in self.mappings:
            if sample[self.target_position] in mapping:
                # have to convert to list as tuples are immutable
                sample = list(sample)
                sample[self.target_position] = mapping.new_label
            if sample[self.tag_position] in mapping:
                # have to convert to list as tuples are immutable
                sample = list(sample)
                sample[self.tag_position] = mapping.new_label
        return tuple(sample)


class FeatureEncoderPostProcessor(FittablePostProcessorIf):

    def __init__(self, sample_position: int, feature_encoding_configs: Dict[str, List[Any]], custom_encoders: Dict[str, Encoder] = None, sequential=False):
        self.sample_position = sample_position
        self.feature_encoding_configs = feature_encoding_configs
        self.feature_encoder_mapping: Dict[str, Encoder] = {"categorical": CategoricalEncoder, "continuous": ContinuousEncoder}
        if custom_encoders is not None:
            self.feature_encoder_mapping = {**self.feature_encoder_mapping, **custom_encoders}
        self.encoders: Dict[int, Encoder] = {}
        self.sequential = sequential

    def fit(self, iterators: Dict[str, DatasetIteratorIF]):

        def fit_sequential(iterators: Dict[str, DatasetIteratorIF]):
            encoders = {}
            for config in tqdm.tqdm(self.feature_encoding_configs, desc="Encoding Progress"):
                encoder_class = self.feature_encoder_mapping[config["feature_type"]]
                feature_indices = config["feature_names"]
                iterator = iterators[config["train_split"]]
                for feature_indice in tqdm.tqdm(feature_indices, desc="Feature type encoding"):
                    values = np.array([row[self.sample_position][feature_indice] for row in iterator])
                    encoder = encoder_class()
                    encoder.fit(values=values)
                    encoders[feature_indice] = encoder
            return encoders

        def fit_parallel(iterators: Dict[str, DatasetIteratorIF]):
            encoders = {}
            for config in tqdm.tqdm(self.feature_encoding_configs, desc="Encoding Progress"):
                encoder_class = self.feature_encoder_mapping[config["feature_type"]]
                feature_indices = config["feature_names"]
                iterator = iterators[config["train_split"]]
                subset_encoders = [encoder_class() for feature_indice in feature_indices]
                values = np.stack([row[self.sample_position][feature_indices] for row in iterator])

                for i in range(len(subset_encoders)):
                    subset_encoders[i].fit(values=values[:, i])
                    encoders[feature_indices[i]] = subset_encoders[i]
            return encoders

        if self.sequential:
            encoders = fit_sequential(iterators)
        else:
            encoders = fit_parallel(iterators)
        # order the encoders by their keys, as of python 3.6 insertion order equals iteration order
        self.encoders = {name: encoder for name, encoder in sorted(encoders.items(), key=lambda x: x[0])}

    def postprocess(self, sample: Tuple[Any]) -> Tuple[Any]:
        if not self.encoders:
            return sample
        sample = list(sample)  # need to make this a list because index assignment is not possible with tuples
        sample_input: torch.Tensor = sample[self.sample_position]
        sample[self.sample_position] = torch.from_numpy(np.hstack([self.encoders[pos].transform(np.array([val])).flatten()
                                                                   if pos in self.encoders.keys() else val for pos, val in enumerate(sample_input)]))
        return tuple(sample)

    def get_output_pattern(self):
        rep = ""
        lower = 0
        for index, encoder in self.encoders.items():
            upper = lower + encoder.get_output_size()
            rep += f"{index} ({type(encoder)}): {lower}, {upper} \n"
        return rep


class OneHotEncodedTargetPostProcessor(PostProcessorIf):

    def __init__(self, target_vector_size: int, target_position: int = 1):
        self.target_vector_size = target_vector_size
        self.target_position = target_position

    def postprocess(self, sample: Tuple[Any]) -> Tuple[Any]:
        target_vector = torch.zeros(self.target_vector_size)
        target_vector[sample[self.target_position]] = 1
        sample_list = list(sample)
        sample_list[self.target_position] = target_vector
        return tuple(sample_list)
