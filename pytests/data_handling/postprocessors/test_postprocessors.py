import pytest
from typing import Tuple
from data_stack.dataset.iterator import InformedDatasetIterator
from data_stack.dataset.meta import IteratorMeta, DatasetMeta
from ml_gym.data_handling.postprocessors.feature_encoder import CategoricalEncoder, ContinuousEncoder
from ml_gym.data_handling.postprocessors.postprocessor import OneHotEncodedTargetPostProcessor, \
    LabelMapperPostProcessor, FeatureEncoderPostProcessor
from pytests.data_handling.postprocessors.mocked_class import MockedIterator


class TestFeatureEncoderPostProcessor:
    @pytest.fixture
    def iterators(self):
        iterator = MockedIterator()
        iterator_meta = IteratorMeta(sample_pos=0, target_pos=1, tag_pos=2)
        dataset_meta = DatasetMeta(identifier="identifier", dataset_name="dataset_name",
                                   dataset_tag="dataset_tag", iterator_meta=iterator_meta)
        iterator = InformedDatasetIterator(iterator, dataset_meta)
        iterators = {"train": iterator, "test": iterator}
        return iterators

    @pytest.fixture
    def sample(self, iterators):
        return iterators["train"][0]

    @pytest.fixture
    def sample_position(self, iterators):
        sample_position = iterators["train"].dataset_meta.sample_pos
        return sample_position

    @pytest.fixture
    def custom_encoders(self):
        custom_encoders = {"categorical2": CategoricalEncoder, "continuous2": ContinuousEncoder}
        return custom_encoders

    @pytest.mark.parametrize('sequential', [True, False])
    def test_postprocess(self, iterators, sample_position, sample, custom_encoders, sequential):
        feature_encoding_configs = [
            {"feature_type": "categorical2", "feature_names": [0, 1, 2], "train_split": "train"},
            {"feature_type": "continuous2", "feature_names": [3, 4], "train_split": "train"},
        ]

        feature_encoder_post_processor = FeatureEncoderPostProcessor(sample_position=sample_position,
                                                                     feature_encoding_configs=feature_encoding_configs,
                                                                     custom_encoders=custom_encoders,
                                                                     sequential=sequential
                                                                     )
        feature_encoder_post_processor.fit(iterators)

        postprocess_sample = feature_encoder_post_processor.postprocess(sample=sample)

        rep = feature_encoder_post_processor.get_output_pattern()
        encoded_vector_length = 0
        for index, encoder in feature_encoder_post_processor.encoders.items():
            encoded_vector_length += encoder.get_output_size()

        # the first three columns are encoded into three 10-dim vectors
        assert len(postprocess_sample[0]) == len(sample[0]) - len(
            feature_encoding_configs[0]["feature_names"]) - len(
            feature_encoding_configs[1]["feature_names"]) + encoded_vector_length
        # The first three columns are encoded by CategoricalEncoder,
        # the values of each column are transformed to 1, because all the values in one column are the same.
        assert postprocess_sample[0][sample[0][0]] == 1
        assert postprocess_sample[0][sample[0][1]] == 1
        assert postprocess_sample[0][sample[0][2]] == 1
        # The last two columns are encoded by ContinuousEncoder,
        # the values of each column are transformed to 0, because all the values in one column are the same
        assert postprocess_sample[0][sample[0][3]] == 0
        assert postprocess_sample[0][sample[0][4]] == 0


class TestOneHotEncodedTargetPostProcessor:

    @pytest.fixture
    def sample(self) -> str:
        return (None, 5, None)  # sample tuple with input, target, tag

    def test_postprocess(self, sample: Tuple):
        postprocessor = OneHotEncodedTargetPostProcessor(target_vector_size=10, target_position=1)
        sample_postprocessed = postprocessor.postprocess(sample)
        assert len(sample_postprocessed[1]) == 10 and sample_postprocessed[1][sample[1]] == 1


class TestLabelMapperPostProcessor:

    @pytest.fixture
    def sample(self) -> str:
        return (None, 5, 4)  # sample tuple with input, target, tag

    def test_postprocess(self, sample: Tuple):
        postprocessor = LabelMapperPostProcessor(mappings=[{"previous_labels": [5], "new_label": 1},
                                                           {"previous_labels": [4], "new_label": 0}],
                                                 target_position=1,
                                                 tag_position=2)
        sample_postprocessed = postprocessor.postprocess(sample)
        assert sample_postprocessed[1] == 1 and sample_postprocessed[2] == 0
