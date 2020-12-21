from typing import Callable, Dict, Any
from functools import partial
from ml_gym.metrics.metrics import PredictionMetric
from ml_gym.batching.batch import InferenceResultBatch


class MetricFactory:

    @staticmethod
    def get_sklearn_metric(metric_key: str, metric_fun: Callable,  params: Dict = None) -> Callable[[InferenceResultBatch], Any]:
        if params is None:
            params = {}
        return partial(PredictionMetric, identifier=metric_key, metric_fun=metric_fun, **params)
