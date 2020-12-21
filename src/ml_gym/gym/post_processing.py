import torch
from torch import nn
from abc import ABC, abstractmethod
from ml_gym.batching.batch import InferenceResultBatch


class PredictPostProcessingIF(ABC):

    @abstractmethod
    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        raise NotImplementedError


class PredictPostProcessing(PredictPostProcessingIF):

    def __init__(self, postprocessing_impl: PredictPostProcessingIF):
        self.postprocessing_impl = postprocessing_impl

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        return self.postprocessing_impl.postprocess(result_batch)


# Postprocessing Implementations

class SoftmaxPostProcessorImpl(PredictPostProcessingIF):
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        predictions = nn.Softmax(dim=1)(result_batch.get_predictions(self.prediction_subscription_key))
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=predictions)
        return result_batch


class ArgmaxPostProcessorImpl(PredictPostProcessingIF):
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        predictions = torch.argmax(result_batch.get_predictions(self.prediction_subscription_key), dim=1)
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=predictions)
        return result_batch


class BinarizationPostProcessorImpl(PredictPostProcessingIF):
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str, threshold=0.5):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key
        self.threshold = threshold

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        predictions = result_batch.get_predictions(self.prediction_subscription_key)
        binarized_outputs = torch.zeros_like(predictions).int()
        binarized_outputs[predictions > self.threshold] = 1
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=binarized_outputs)
        return result_batch


class SigmoidalPostProcessorImpl(PredictPostProcessingIF):
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str, threshold=0.5):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        predictions = result_batch.get_predictions(self.prediction_subscription_key)
        sigmoidal_predictions = torch.sigmoid(predictions)
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=sigmoidal_predictions)
        return result_batch


class DummyPostProcessorImpl(PredictPostProcessingIF):

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        return result_batch
