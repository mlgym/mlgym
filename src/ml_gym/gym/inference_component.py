from ml_gym.models.nn.net import NNModel
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from typing import List
from ml_gym.util.timer import timeit_ns
import torch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
import tqdm
from ml_gym.data_handling.dataset_loader import DatasetLoader


class InferenceComponent:
    def __init__(self, no_grad=True):
        self.no_grad = no_grad

    @timeit_ns
    def predict(self, model: NNModel, batch: DatasetBatch, post_processors: List[PredictPostProcessingIF] = None) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model.

        :params:
               model (NNModel): Torch Neural Network module.
               batch (DatasetBatch): Train Dataset.
               post_processors (List[PredictPostProcessingIF]): Batch number for which details to be logged.
           
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        post_processors = post_processors if post_processors is not None else []
        if self.no_grad:
            with torch.no_grad():
                forward_result = model.forward(batch.samples)
        else:
            forward_result = model.forward(batch.samples)
        result_batch = InferenceResultBatch(targets=batch.targets, tags=batch.tags, predictions=forward_result)
        return PredictPostprocessingComponent.post_process(result_batch, post_processors=post_processors)

    def predict_data_loader(self, model: NNModel, dataset_loader: DatasetLoader) -> InferenceResultBatch:
        """
        Perform prediction on the batches from dataset_loader using the torch NN Model.

        :params:
               model (NNModel): Torch Neural Network module.
               dataset_loader (DatasetLoader): Dataset loader.
           
        :returns:
            InferenceResultBatch object: Combination of all predictions performed on the batches.
        """
        result_batches = [self.predict(model, batch) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)
