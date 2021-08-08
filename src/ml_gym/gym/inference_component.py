from ml_gym.models.nn.net import NNModel
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from typing import List
import torch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
import tqdm
from ml_gym.data_handling.dataset_loader import DatasetLoader


class InferenceComponent:
    def __init__(self, no_grad=True):
        self.no_grad = no_grad

    def predict(self, model: NNModel, batch: DatasetBatch, post_processors: List[PredictPostProcessingIF] = None) -> InferenceResultBatch:
        post_processors = post_processors if post_processors is not None else []
        if self.no_grad:
            with torch.no_grad():
                forward_result = model.forward(batch.samples)
        else:
            forward_result = model.forward(batch.samples)
        result_batch = InferenceResultBatch(targets=batch.targets, tags=batch.tags, predictions=forward_result)
        return PredictPostprocessingComponent.post_process(result_batch, post_processors=post_processors)

    def predict_data_loader(self, model: NNModel, dataset_loader: DatasetLoader) -> InferenceResultBatch:
        result_batches = [self.predict(model, batch) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)
