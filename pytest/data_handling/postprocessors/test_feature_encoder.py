import numpy as np
import pytest
import torch
from ml_gym.data_handling.postprocessors.feature_encoder import ContinuousEncoder, CategoricalEncoder


class TestCategoricalEncoder:
    @pytest.fixture
    def encoder(self) -> CategoricalEncoder:
        encoder = CategoricalEncoder()
        return encoder

    @pytest.fixture
    def values(self):
        values = np.array([0, 1, 2, 1, 2, 1, 2, 0])
        return torch.from_numpy(values)

    @pytest.mark.parametrize("sample",
                             [[0],
                              [1],
                              [2],
                              pytest.param([3], marks=pytest.mark.xfail),
                              ])
    def test_fit_and_transform(self, encoder, values, sample):
        sample = np.array(sample)
        encoder.fit(values)
        transformed_sample = encoder.transform(sample)
        assert transformed_sample[0][sample[0]] == 1
        # only one value in this vector is 1
        assert np.sum(transformed_sample) == 1
        assert encoder.get_output_size() == len(torch.bincount(values))


class TestContinuousEncoder:
    @pytest.fixture
    def encoder(self):
        encoder = ContinuousEncoder()
        return encoder

    @pytest.fixture
    def values(self):
        values = np.linspace(0, 10, 50)
        return values

    @pytest.mark.parametrize("sample_value",
                             [0.5, 1, 2.6
                              ])
    def test_fit_and_transform(self, encoder, values, sample_value):
        encoder.fit(values)
        transformed_values = encoder.transform(values)
        # the mean of StandardScaler == 0
        assert np.mean(transformed_values, axis=1)[0] < 1e-8
        # the std of StandardScaler == 1
        assert np.std(transformed_values, axis=1)[0] - 1 < 1e-8
        # StandardScaler does (x - mean )/ std
        assert (sample_value - np.mean(values)) / np.std(values) == encoder.transform(np.array([sample_value]))[0][0]
        assert encoder.get_output_size() == 1
