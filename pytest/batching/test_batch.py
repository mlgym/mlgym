from typing import List, Union

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
        predictions = {"a": torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1]),
                       "b": {"b_1": torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1]),
                             "b_2": torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1])}
                       }
        return InferenceResultBatch(targets={TestInferenceResultBatch.target_key: targets},
                                    predictions=predictions,
                                    tags=tags)

    @pytest.fixture
    def target_keys(self) -> List[str]:
        return None

    @pytest.fixture
    def predictions_keys(self) -> List[Union[str, List]]:
        return

    @pytest.fixture
    def device(self) -> torch.device:
        return

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

    @pytest.mark.parametrize("target_keys, predictions_keys, target_num, predictions_num",
                             [
                                 (["*"], ["*"], 0, 2),
                                 (["target_key"], ["*"], 1, 2),
                                 (["_____"], ["a", "b"], 0, 2),
                                 (["target_key"], ["a", "b"], 1, 2),
                                 pytest.param(["target_key"], ["_", "b"], 1, 1, marks=pytest.mark.xfail),
                             ])
    def test_split_results(self, inference_batch_result, target_keys, predictions_keys, target_num, predictions_num):
        filtered_inference_batch_result = inference_batch_result.split_results(target_keys, predictions_keys,
                                                                               torch.device("cpu"))
        assert len(filtered_inference_batch_result.targets) == target_num
        assert len(filtered_inference_batch_result.predictions) == predictions_num


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
