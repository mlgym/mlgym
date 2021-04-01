from ml_gym.models.nn.net import NNModel
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from typing import List
import torch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
import tqdm
from ml_gym.data_handling.dataset_loader import DatasetLoader
from copy import deepcopy


class ExportedModel:
    def __init__(self, model: NNModel, post_processors: List[PredictPostProcessingIF]):
        self.post_processors = post_processors
        self.model = model

    def predict_tensor(self, sample_tensor: torch.Tensor):
        with torch.no_grad():
            forward_result = self.model.forward(sample_tensor)
        result_batch = InferenceResultBatch(targets=None, tags=None, predictions=forward_result)
        return PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)

    def predict_dataset_batch(self, batch: DatasetBatch) -> InferenceResultBatch:
        with torch.no_grad():
            forward_result = self.model.forward(batch.samples)
        result_batch = InferenceResultBatch(targets=deepcopy(batch.targets), tags=deepcopy(batch.tags), predictions=forward_result)
        return PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)

    def predict_data_loader(self, dataset_loader: DatasetLoader) -> InferenceResultBatch:
        result_batches = [self.predict_dataset_batch(batch) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)


class InferenceComponent:
    def __init__(self, post_processors: List[PredictPostProcessingIF], no_grad=True):
        self.post_processors = post_processors
        self.no_grad = no_grad

    def predict(self, model: NNModel, batch: DatasetBatch) -> InferenceResultBatch:
        if self.no_grad:
            with torch.no_grad():
                forward_result = model.forward(batch.samples)
        else:
            forward_result = model.forward(batch.samples)
        result_batch = InferenceResultBatch(targets=batch.targets, tags=batch.tags, predictions=forward_result)
        return PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)

    def predict_data_loader(self, model: NNModel, dataset_loader: DatasetLoader) -> InferenceResultBatch:
        result_batches = [self.predict(model, batch) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)

    # TODO, this is really just a temporary hack and should be done at a different place!
    def export_model(self, model: NNModel) -> ExportedModel:
        return ExportedModel(model, self.post_processors)
