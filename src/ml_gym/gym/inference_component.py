from ml_gym.models.nn.net import NNModel
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from typing import List
import torch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF


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
