import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch


class TestInferenceResultBatch:
    target_key = "target_key"
    prediction_key = "prediction_key"

    @pytest.fixture
    def inference_batch_result(self) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 1, 1])
        tags = torch.IntTensor([0, 0, 0, 1, 1, 1])
        predictions = torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1])
        return InferenceResultBatch(targets={TestInferenceResultBatch.target_key: targets},
                                    predictions={TestInferenceResultBatch.prediction_key: predictions},
                                    tags=tags)

    # test device operations
    def test_to_device(self, inference_batch_result: InferenceResultBatch):
        inference_batch_result.to_device(torch.device("cpu"))

    def test_to_cpu(self, inference_batch_result: InferenceResultBatch):
        inference_batch_result.to_cpu()

    def test_get_device(self, inference_batch_result: InferenceResultBatch):
        inference_batch_result.to_device(torch.device("cpu"))
        assert inference_batch_result.get_device() == torch.device("cpu")

    def test_detach(self, inference_batch_result: InferenceResultBatch):
        inference_batch_result.detach()


class TestDatasetBatch:
    target_key = "target_key"
    prediction_key = "prediction_key"

    @pytest.fixture
    def dataset_batch(self) -> DatasetBatch:
        tensor = torch.IntTensor([0, 0, 0, 1, 1, 1])
        return DatasetBatch(targets={TestDatasetBatch.target_key: tensor.clone()},
                            samples=tensor.clone(),
                            tags=tensor.clone())

    # test device operations
    def test_to_device(self, dataset_batch: DatasetBatch):
        dataset_batch.to_device(torch.device("cpu"))

    def test_to_cpu(self, dataset_batch: DatasetBatch):
        dataset_batch.to_cpu()

    def test_get_device(self, dataset_batch: DatasetBatch):
        dataset_batch.to_device(torch.device("cpu"))
        assert dataset_batch.get_device() == torch.device("cpu")

    def test_detach(self, dataset_batch: DatasetBatch):
        dataset_batch.detach()
