import pytest
from typing import Tuple
from ml_gym.data_handling.postprocessors.postprocessor import OneHotEncodedTargetPostProcessor, LabelMapperPostProcessor


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
