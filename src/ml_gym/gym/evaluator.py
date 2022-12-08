from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Union
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.persistency.logging import ExperimentStatusLogger
import torch
from ml_gym.batching.batch import DatasetBatch, EvaluationBatchResult, InferenceResultBatch
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.metrics.metrics import Metric
from ml_gym.models.nn.net import NNModel
from ml_gym.loss_functions.loss_functions import Loss
import tqdm
from ml_gym.util.logger import ConsoleLogger
import numpy as np
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.error_handling.exception import BatchStateError, EvaluationError, MetricCalculationError, LossCalculationError


class AbstractEvaluator(StatefulComponent):
    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device, epoch: int) -> List[EvaluationBatchResult]:
        raise NotImplementedError


class Evaluator(AbstractEvaluator):
    def __init__(self, eval_component: 'EvalComponentIF'):
        self.eval_component = eval_component
        self.current_epoch = -1
        self.num_epochs = -1

    def set_num_epochs(self, num_epochs: int):
        self.num_epochs = num_epochs

    def evaluate(self, model: NNModel, device: torch.device, current_epoch: int, num_epochs: int,
                 epoch_result_callback_fun: Callable = None,
                 batch_processed_callback_fun: Callable = None) -> List[EvaluationBatchResult]:
        self.current_epoch = current_epoch
        self.num_epochs = num_epochs
        # returns a EvaluationBatchResult for each split
        evaluation_batch_results = self.eval_component.evaluate(model, device, epoch_result_callback_fun=epoch_result_callback_fun,
                                                                batch_processed_callback_fun=batch_processed_callback_fun)
        return evaluation_batch_results


class EvalComponentIF(StatefulComponent):

    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device, epoch_result_callback_fun: Callable = None,
                 batch_processed_callback_fun: Callable = None) -> List[EvaluationBatchResult]:
        raise NotImplementedError


class EvalComponent(EvalComponentIF):
    """This thing always comes with batteries included, i.e., datasets, loss functions etc. are all already stored in here."""

    def __init__(self, inference_component: InferenceComponent, post_processors: Dict[str, PredictPostprocessingComponent], metrics: List[Metric],
                 loss_funs: Dict[str, Loss], dataset_loaders: Dict[str, DatasetLoader], train_split_name: str, show_progress: bool = False,
                 cpu_target_subscription_keys: List[str] = None, cpu_prediction_subscription_keys: List[Union[str, List]] = None,
                 metrics_computation_config: List[Dict] = None, loss_computation_config: List[Dict] = None):
        self.loss_funs = loss_funs
        self.inference_component = inference_component
        # maps split names to postprocessors
        self.post_processors = post_processors
        self.metrics = metrics
        self.dataset_loaders = dataset_loaders
        self.train_split_name = train_split_name
        self.show_progress = show_progress
        self.cpu_target_subscription_keys = cpu_target_subscription_keys
        self.cpu_prediction_subscription_keys = cpu_prediction_subscription_keys
        self.logger = ConsoleLogger("logger_eval_component")
        # determines which metrics are applied to which splits (metric_key to split list)
        self.metrics_computation_config = None if metrics_computation_config is None else {
            m["metric_tag"]: m["applicable_splits"] for m in metrics_computation_config}
        # determines which losses are applied to which splits (loss_key to split list)
        self.loss_computation_config = None if loss_computation_config is None else {
            m["loss_tag"]: m["applicable_splits"] for m in loss_computation_config}
        self.experiment_status_logger: ExperimentStatusLogger = None

    def evaluate(self, model: NNModel, device: torch.device, epoch_result_callback_fun: Callable = None,
                 batch_processed_callback_fun: Callable = None) -> List[EvaluationBatchResult]:
        return [self.evaluate_dataset_split(model, device, split_name, loader, epoch_result_callback_fun, batch_processed_callback_fun) for split_name, loader in self.dataset_loaders.items()]

    def evaluate_dataset_split(self, model: NNModel, device: torch.device, split_name: str,
                               dataset_loader: DatasetLoader, epoch_result_callback_fun: Callable = None,
                               batch_processed_callback_fun: Callable = None) -> EvaluationBatchResult:
        dataset_loader.device = device
        dataset_loader_iterator = tqdm.tqdm(
            dataset_loader, desc=f"Evaluating {dataset_loader.dataset_name} - {split_name}") if self.show_progress else dataset_loader
        post_processors = self.post_processors[split_name] + self.post_processors["default"]

        # calc losses
        if self.loss_computation_config is not None:
            loss_tags = [loss_tag for loss_tag, applicable_splits in self.loss_computation_config.items()
                         if split_name in applicable_splits]
            split_loss_funs = {tag: loss_fun for tag, loss_fun in self.loss_funs.items() if tag in loss_tags}
        else:
            split_loss_funs = self.loss_funs

        batch_losses = []
        inference_result_batches_cpu = []
        num_batches = len(dataset_loader_iterator)
        processed_batches = 0
        update_lag = int(num_batches/10)
        for batch in dataset_loader_iterator:
            inference_result_batch = self.forward_batch(dataset_batch=batch, model=model, device=device, postprocessors=post_processors)
            batch_loss = self._calculate_loss_scores(inference_result_batch, split_loss_funs)
            batch_losses.append(batch_loss)
            irb_filtered = inference_result_batch.split_results(predictions_keys=self.cpu_prediction_subscription_keys,
                                                                target_keys=self.cpu_target_subscription_keys,
                                                                device=torch.device("cpu"))
            inference_result_batches_cpu.append(irb_filtered)
            processed_batches += 1
            if batch_processed_callback_fun is not None and (processed_batches % update_lag == 0 or processed_batches == num_batches):
                splits = [d.dataset_tag for _, d in self.dataset_loaders.items()]
                batch_processed_callback_fun(status="evaluation",
                                             num_batches=num_batches,
                                             current_batch=processed_batches,
                                             splits=splits,
                                             current_split=dataset_loader.dataset_tag)

        # calc metrics
        try:
            prediction_batch = InferenceResultBatch.combine(inference_result_batches_cpu)
        except BatchStateError as e:
            raise EvaluationError(f"Error combining inference result batch on split {split_name}.") from e

        # select metrics for split
        if self.metrics_computation_config is not None:
            metric_tags = [metric_tag for metric_tag, applicable_splits in self.metrics_computation_config.items()
                           if split_name in applicable_splits]
            split_metrics = [metric for metric in self.metrics if metric.tag in metric_tags]
        else:
            split_metrics = self.metrics
        metric_scores = self._calculate_metric_scores(prediction_batch, split_metrics)

        # aggregate losses
        loss_keys = batch_losses[0].keys()
        loss_scores = {key: [np.mean([l[key] for l in batch_losses])] for key in loss_keys}

        evaluation_result = EvaluationBatchResult(losses=loss_scores,
                                                  metrics=metric_scores,
                                                  dataset_name=dataset_loader.dataset_name,
                                                  split_name=split_name)
        if epoch_result_callback_fun is not None:
            epoch_result_callback_fun(evaluation_result=evaluation_result)
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
        metric_scores = {}
        for metric in split_metrics:
            try:
                metric_scores[metric.tag] = [metric(inference_batch)]
            except Exception as e:
                raise MetricCalculationError(f"Error during calculation of metric {metric.tag}") from e
        return metric_scores

    def _calculate_loss_scores(self, forward_batch: InferenceResultBatch, split_loss_funs: Dict[str, Loss]) -> Dict[str, List[float]]:
        loss_scores = {}
        for loss_key, loss_fun in split_loss_funs.items():
            try:
                loss_scores[loss_key] = self._get_batch_loss(loss_fun, forward_batch)
            except Exception as e:
                raise LossCalculationError("Error during calculation of loss {loss_key}") from e

        return loss_scores

    def _get_batch_loss(self, loss_fun: Loss, forward_batch: InferenceResultBatch) -> List[float]:
        loss = loss_fun(forward_batch)
        loss = [loss.sum().detach().item()]
        return loss
