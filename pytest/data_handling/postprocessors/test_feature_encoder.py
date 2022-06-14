import numpy as np
import pytest
import torch
from src.ml_gym.data_handling.postprocessors.feature_encoder import ContinuousEncoder, CategoricalEncoder



class TestCategoricalEncoder:
    @pytest.fixture
    def encoder(self) -> CategoricalEncoder:
        encoder = CategoricalEncoder()
        return encoder

    @pytest.fixture
    def values(self):
        values = torch.randint(0, 10, (50,))
        return values

    @pytest.fixture
    def sample(self):
        return np.array([1])

    def test_fit_and_transform(self, encoder, values, sample):
        encoder.fit(values)
        transformed_sample = encoder.transform(sample)
        assert transformed_sample[0][sample[0]] == 1
        assert encoder.get_output_size() <= 10


class TestContinuousEncoder:
    @pytest.fixture
    def encoder(self):
        encoder = ContinuousEncoder()
        return encoder

    @pytest.fixture
    def values(self):
        values = torch.rand(50).float()
        return values

    @pytest.fixture
    def sample(self):
        return [0.5]

    def test_fit_and_transform(self, encoder, values, sample):
        encoder.fit(values)
        transformed_sample = encoder.transform(sample)
        assert transformed_sample[0][0] < 1
        assert encoder.get_output_size() == 1
