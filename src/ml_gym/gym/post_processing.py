import torch
from torch import nn
from abc import ABC, abstractmethod
from ml_gym.batching.batch import InferenceResultBatch


class PredictPostProcessingIF(ABC):
    """
    Interface to perform prediction on the torch NN Model for the entire btach.
    """

    @abstractmethod
    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        raise NotImplementedError


class PredictPostProcessing(PredictPostProcessingIF):
    """
    Class providing function to perform prediction on the torch NN Model for the entire btach.
    """

    def __init__(self, postprocessing_impl: PredictPostProcessingIF):
        self.postprocessing_impl = postprocessing_impl

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        return self.postprocessing_impl.postprocess(result_batch)


# Postprocessing Implementations

class SoftmaxPostProcessorImpl(PredictPostProcessingIF):
    """
    Class to perform prediction on the torch NN Model for the entire btach using SoftMax.
    """
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach using SoftMax.

        :params:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        predictions = nn.Softmax(dim=1)(result_batch.get_predictions(self.prediction_subscription_key))
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=predictions)
        return result_batch


class ArgmaxPostProcessorImpl(PredictPostProcessingIF):
    """
    Class to perform prediction on the torch NN Model for the entire btach using ArgMax.
    """
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach using ArgMax.

        :params:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        predictions = torch.argmax(result_batch.get_predictions(self.prediction_subscription_key), dim=1)
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=predictions)
        return result_batch


class MaxOrMinPostProcessorImpl(PredictPostProcessingIF):
    """
    Class to perform prediction on the torch NN Model for the entire btach using Max and Min.
    """
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str, agg_fun: str):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key
        if agg_fun == "max":
            self.agg_fun = torch.max
        elif agg_fun == "min":
            self.agg_fun = torch.min
        else:
            raise NotImplementedError("agg_fun={agg_fun} is not an applicable parameter")

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach using Max and Min.

        :params:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        predictions = self.agg_fun(result_batch.get_predictions(self.prediction_subscription_key), dim=1)[0]
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=predictions)
        return result_batch


class BinarizationPostProcessorImpl(PredictPostProcessingIF):
    """
    Class to perform prediction on the torch NN Model for the entire btach using Zero Like Binarizaton.
    """
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str, threshold=0.5):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key
        self.threshold = threshold

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach using Zero Like Binarizaton.

        :params:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        predictions = result_batch.get_predictions(self.prediction_subscription_key)
        binarized_outputs = torch.zeros_like(predictions).int()
        binarized_outputs[predictions > self.threshold] = 1
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=binarized_outputs)
        return result_batch


class SigmoidalPostProcessorImpl(PredictPostProcessingIF):
    """
    Class to perform prediction on the torch NN Model for the entire btach using Sigmoid.
    """
    def __init__(self, prediction_subscription_key: str, prediction_publication_key: str, threshold=0.5):
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach using Sigmoid.

        :params:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        predictions = result_batch.get_predictions(self.prediction_subscription_key)
        sigmoidal_predictions = torch.sigmoid(predictions)
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=sigmoidal_predictions)
        return result_batch


class DummyPostProcessorImpl(PredictPostProcessingIF):

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        return result_batch