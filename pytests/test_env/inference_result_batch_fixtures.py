import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch

from pytests.test_env.component_fixtures import Keys


class InferenceBatchResultFixture(Keys):
    @pytest.fixture
    def target_key(self, target_key_anchor) -> str:
        return target_key_anchor

    @pytest.fixture
    def prediction_publication_key(self, model_prediction_key_anchor: str) -> str:
        return model_prediction_key_anchor

    @pytest.fixture
    def prediction_subscription_key(self, model_prediction_key_anchor: str) -> str:
        return model_prediction_key_anchor

    @pytest.fixture
    def inference_batch_result1(self, target_key, prediction_publication_key) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 1, 1])
        tags = torch.IntTensor([0, 0, 0, 1, 1, 1])
        predictions = {prediction_publication_key: torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1])
                       }
        return InferenceResultBatch(targets={target_key: targets},
                                    predictions=predictions,
                                    tags=tags)

    @pytest.fixture
    def inference_batch_result2(self, target_key, prediction_publication_key) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 1, 1])
        tags = torch.IntTensor([0, 0, 0, 1, 1, 1])
        predictions = {
            prediction_publication_key: torch.FloatTensor(
                [[0, 0.1], [0.1, 0.12], [0.01, 0.08], [0, 0.9], [0.1, 0.7], [1, 0]])
        }
        return InferenceResultBatch(targets={target_key: targets},
                                    predictions=predictions,
                                    tags=tags)
