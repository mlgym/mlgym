from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List
from ml_gym.gym.post_processing import PredictPostProcessingIF
import torch
from ml_gym.batching.batch import DatasetBatch, EvaluationBatchResult, InferenceResultBatch
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.metrics.metrics import Metric
from ml_gym.models.nn.net import NNModel
from ml_gym.loss_functions.loss_functions import Loss, LossWarmupMixin
import tqdm
from ml_gym.util.logger import ConsoleLogger
import numpy as np
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent


class AbstractEvaluator(StatefulComponent):
    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError

    # @abstractmethod
    # def warm_up(self, model: NNModel, device: torch.device):
    #     raise NotImplementedError


class Evaluator(AbstractEvaluator):
    def __init__(self, eval_component: 'EvalComponentIF'):
        self.eval_component = eval_component

    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        return self.eval_component.evaluate(model, device)

    # def warm_up(self, model: NNModel, device: torch.device):
    #     self.eval_component.warm_up(model, device)


class EvalComponentIF(StatefulComponent):
    # @abstractmethod
    # def warm_up(self, model: NNModel, device: torch.device):
    #     raise NotImplementedError

    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError


class EvalComponent(EvalComponentIF):
    """This thing always comes with batteries included, i.e., datasets, loss functions etc. are all already stored in here."""

    def __init__(self, inference_component: InferenceComponent, post_processors: Dict[str, PredictPostprocessingComponent], metrics: List[Metric],
                 loss_funs: Dict[str, Loss], dataset_loaders: Dict[str, DatasetLoader], train_split_name: str, show_progress: bool = False,
                 cpu_target_subscription_keys: List[str] = None, cpu_prediction_subscription_keys: List[str] = None, 
                 metrics_computation_config: List[Dict] = None, loss_computation_config: List[Dict] = None):
        self.loss_funs = loss_funs
        self.inference_component = inference_component
        # maps split names to postprocessors
        self.post_processors = post_processors
        self.metrics = metrics
        self.dataset_loaders = dataset_loaders
        self.train_split_name = train_split_name
        self.show_progress = show_progress
        self.cpu_target_subscription_keys = set(cpu_target_subscription_keys)
        self.cpu_prediction_subscription_keys = set(cpu_prediction_subscription_keys)
        self.logger = ConsoleLogger("logger_eval_component")
        # determines which metrics are applied to which splits (metric_key to split list)
        if metrics_computation_config is None:
            self.metrics_computation_config = None 
        else:
            self.metrics_computation_config = {m["metric_tag"]: m["applicable_splits"] for m in metrics_computation_config}
        self.loss_computation_config = loss_computation_config

    # def warm_up(self, model: NNModel, device: torch.device):
    #     def init_loss_funs(batch: InferenceResultBatch):
    #         for _, loss_fun in self.loss_funs.items():
    #             if isinstance(loss_fun, LossWarmupMixin):
    #                 loss_fun.warm_up(batch)
    #                 loss_fun.finish_warmup()

    #     if any([isinstance(loss_fun, LossWarmupMixin) for _, loss_fun in self.loss_funs.items()]):
    #         self.logger.log(LogLevel.INFO, "Running warmup...")
    #         prediction_batches = self.map_batches(fun=self.forward_batch,
    #                                               fun_params={"calculation_device": device, "model": model,
    #                                                           "result_device": torch.device("cpu")},
    #                                               loader=self.dataset_loaders[self.train_split_name],
    #                                               show_progress=self.show_progress)
    #         prediction_batch = InferenceResultBatch.combine(prediction_batches)
    #         init_loss_funs(prediction_batch)
    #     else:
    #         self.logger.log(LogLevel.INFO, "Skipping evaluation warmup. No special loss functions to be initialized.")

    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        return [self.evaluate_dataset_split(model, device, split_name, loader) for split_name, loader in self.dataset_loaders.items()]

    def evaluate_dataset_split(self, model: NNModel, device: torch.device, split_name: str, dataset_loader: DatasetLoader) -> EvaluationBatchResult:
        if self.show_progress:
            dataset_loader = tqdm.tqdm(dataset_loader, desc="Batches processed:")
        post_processors = self.post_processors[split_name]
        batch_losses = []
        inference_result_batches_cpu = []
        for batch in dataset_loader:
            inference_result_batch = self.forward_batch(dataset_batch=batch, model=model, device=device, postprocessors=post_processors)
            batch_loss = self._calculate_loss_scores(inference_result_batch)
            batch_losses.append(batch_loss)
            irb_filtered = inference_result_batch.split_results(predictions_keys=self.cpu_prediction_subscription_keys,
                                                                target_keys=self.cpu_target_subscription_keys,
                                                                device=torch.device("cpu"))
            inference_result_batches_cpu.append(irb_filtered)

        # calc metrics
        prediction_batch = InferenceResultBatch.combine(inference_result_batches_cpu)
        # select metrics for split
        if self.metrics_computation_config is not None:
            metric_tags = [metric_tag for metric_tag, applicable_splits in self.metrics_computation_config.items() if split_name in applicable_splits]
            split_metrics = [metric for metric in self.metrics if metric.tag in metric_tags]
        else: 
            split_metrics = self.metrics
        metric_scores = self._calculate_metric_scores(prediction_batch, split_metrics)

        # calc losses
        loss_keys = batch_losses[0].keys()
        loss_scores = {key: [np.mean([l[key] for l in batch_losses])] for key in loss_keys}

        evaluation_result = EvaluationBatchResult(losses=loss_scores,
                                                  metrics=metric_scores,
                                                  dataset_name=dataset_loader.dataset_name,
                                                  split_name=split_name)
        return evaluation_result

    def _get_metric_fun(self, identifier: str, target_subscription: Enum, prediction_subscription: Enum,
                        metric_fun: Callable, params: Dict[str, Any]) -> Metric:
        return Metric(identifier, target_subscription, prediction_subscription, metric_fun, params)

    def forward_batch(self, dataset_batch: DatasetBatch, model: NNModel, device: torch.device, postprocessors: List[PredictPostProcessingIF]) -> InferenceResultBatch:
        model = model.to(device)
        dataset_batch.to_device(device)
        inference_result_batch = self.inference_component.predict(model, dataset_batch, postprocessors)
        return inference_result_batch

    def _calculate_metric_scores(self, inference_batch: InferenceResultBatch, split_metrics: List[Metric]) -> Dict[str, List[float]]:
        return {metric.tag: [metric(inference_batch)] for metric in split_metrics}

    def _calculate_loss_scores(self, forward_batch: InferenceResultBatch) -> Dict[str, List[float]]:
        return {loss_key: self._get_batch_loss(loss_fun, forward_batch) for loss_key, loss_fun in self.loss_funs.items()}

    def _get_batch_loss(self, loss_fun: Loss, forward_batch: InferenceResultBatch) -> List[float]:
        loss = loss_fun(forward_batch)
        loss = [loss.detach().item()]
        return loss
