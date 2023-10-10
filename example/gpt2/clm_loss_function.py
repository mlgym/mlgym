from dataclasses import dataclass
from typing import Dict, Any
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.metrics.metrics import Metric
from ml_gym.gym.post_processing import PredictPostProcessingIF, PredictPostProcessing
from ml_gym.batching.batch import InferenceResultBatch
import torch
from torch.nn import CrossEntropyLoss
from ml_gym.blueprints.constructables import LossFunctionRegistryConstructable, MetricFunctionRegistryConstructable, PredictionPostProcessingRegistryConstructable

@dataclass
class LMPredictionPostProcessingRegistryConstructable(PredictionPostProcessingRegistryConstructable):
    class FunctionKeys:
        PerplexityPostProcessing = "PerplexityPostProcessing"
    
    def _construct_impl(self):
        pp_registry = super()._construct_impl()
        default_mapping: Dict[str, Any] = {
            self.FunctionKeys.PerplexityPostProcessing: PerplexityPostProcessing
        }

        for key, loss_type in default_mapping.items():
            pp_registry.add_class(key, loss_type)

        return pp_registry

@dataclass
class LMMetricFunctionRegistryConstructable(MetricFunctionRegistryConstructable):
    class MetricKeys:
        PerplexityMetric = "PerplexityMetric"
    
    def _construct_impl(self):
        metric_registry = super()._construct_impl()
        default_mapping: Dict[str, Any] = {
            self.MetricKeys.PerplexityMetric: PerplexityMetric
        }

        for key, loss_type in default_mapping.items():
            metric_registry.add_class(key, loss_type)

        return metric_registry

@dataclass
class LMLossFunctionRegistryConstructable(LossFunctionRegistryConstructable):
    class LossKeys:
        CLMCrossEntropyLoss = "CLMCrossEntropyLoss"

    def _construct_impl(self):
        loss_fun_registry = super()._construct_impl()
        default_mapping: Dict[str, Any] = {
            self.LossKeys.CLMCrossEntropyLoss: CLMCrossEntropyLoss
        }

        for key, loss_type in default_mapping.items():
            loss_fun_registry.add_class(key, loss_type)

        return loss_fun_registry

class PerplexityPostProcessing(PredictPostProcessingIF):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, prediction_publication_key: str):
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.prediction_publication_key = prediction_publication_key
        self.loss_fun = CrossEntropyLoss()

    def postprocess(self, result_batch: InferenceResultBatch) -> InferenceResultBatch:
        t = result_batch.get_targets(self.target_subscription_key)
        p = result_batch.get_predictions(self.prediction_subscription_key)
        loss = self.loss_fun(p.view(-1, p.size(-1)), t.view(-1))
        result_batch.add_predictions(key=self.prediction_publication_key, predictions=loss)
        return result_batch

class PerplexityMetric(Metric):
    def __init__(self, prediction_subscription_key: str, identifier: str = "" 
                 , tag: str = ""):
        super().__init__(tag=tag, identifier=identifier)
        self.prediction_subscription_key = prediction_subscription_key

    def __call__(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        loss = forward_batch.get_predictions(self.prediction_subscription_key)
        perplexity = torch.exp(torch.mean(loss)).item()
        return perplexity

class CLMCrossEntropyLoss(Loss):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        super().__init__(tag)
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.loss_fun = CrossEntropyLoss()

    def __call__(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        t = forward_batch.get_targets(self.target_subscription_key)
        p = forward_batch.get_predictions(self.prediction_subscription_key)
        casual_lm_loss = self.loss_fun(p.view(-1, p.size(-1)), t.view(-1))
        return casual_lm_loss
