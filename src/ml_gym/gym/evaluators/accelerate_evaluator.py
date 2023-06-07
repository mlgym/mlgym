from enum import Enum
from typing import Any, Callable, Dict, List, Union
from ml_gym.gym.evaluators.evaluator import AbstractEvaluator
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.persistency.logging import ExperimentStatusLogger
import torch
from ml_gym.batching.batch import DatasetBatch, EvaluationBatchResult, InferenceResultBatch
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.metrics.metrics import Metric
from ml_gym.models.nn.net import NNModel
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.error_handling.exception import BatchStateError, EvaluationError, MetricCalculationError, LossCalculationError
from accelerate import Accelerator


class AccelerateEvaluator(AbstractEvaluator):
    def __init__(self, eval_component: "AccelerateEvalComponent"):
        self.eval_component = eval_component

    def evaluate(self, model: NNModel, accelerator: Accelerator, epoch_result_callback_fun: Callable = None,
                 batch_processed_callback_fun: Callable = None) -> List[EvaluationBatchResult]:
        """
        Evaulate torch NN Model.

        :params:
               model (NNModel): Torch Neural Network module
               accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
               epoch_result_callback_fun (Callable): numner of batches to be trained.
               batch_processed_callback_fun (Callable): Batch number for which details to be logged.

        :returns:
            evaluation_batch_results (List[EvaluationBatchResult]): Evaluation results of batches trained on.
        """
        model.eval()

        # returns a EvaluationBatchResult for each split
        evaluation_batch_results = self.eval_component.evaluate(model=model, accelerator=accelerator,
                                                                epoch_result_callback_fun=epoch_result_callback_fun,
                                                                batch_processed_callback_fun=batch_processed_callback_fun)
        return evaluation_batch_results


class AccelerateEvalComponent:
    """This thing always comes with batteries included, i.e., datasets, loss functions etc. are all already stored in here."""

    def __init__(self, inference_component: InferenceComponent, post_processors: Dict[str, PredictPostprocessingComponent], metrics: List[Metric],
                 loss_funs: Dict[str, Loss], dataset_loaders: Dict[str, DatasetLoader],
                 cpu_target_subscription_keys: List[str] = None, cpu_prediction_subscription_keys: List[Union[str, List]] = None,
                 metrics_computation_config: List[Dict] = None, loss_computation_config: List[Dict] = None):
        self.loss_funs = loss_funs
        self.inference_component = inference_component
        # maps split names to postprocessors
        self.post_processors = post_processors
        self.metrics = metrics
        self.dataset_loaders = dataset_loaders
        self.cpu_target_subscription_keys = cpu_target_subscription_keys
        self.cpu_prediction_subscription_keys = cpu_prediction_subscription_keys
        # determines which metrics are applied to which splits (metric_key to split list)
        self.metrics_computation_config = None if metrics_computation_config is None else {
            m["metric_tag"]: m["applicable_splits"] for m in metrics_computation_config}
        # determines which losses are applied to which splits (loss_key to split list)
        self.loss_computation_config = None if loss_computation_config is None else {
            m["loss_tag"]: m["applicable_splits"] for m in loss_computation_config}
        self.experiment_status_logger: ExperimentStatusLogger = None

    def evaluate(self, model: NNModel, accelerator: Accelerator, epoch_result_callback_fun: Callable = None,
                 batch_processed_callback_fun: Callable = None) -> List[EvaluationBatchResult]:
        """
        Evaulate torch NN Model.

        :params:
               model (NNModel): Torch Neural Network module.
               accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
               epoch_result_callback_fun (Callable): numner of batches to be trained.
               batch_processed_callback_fun (Callable): Batch number for which details to be logged.

        :returns:
            evaluation_batch_results (List[EvaluationBatchResult]): Evaluation results of batches trained on.
        """
        return [self.evaluate_dataset_split(model, split_name, loader, accelerator, epoch_result_callback_fun, batch_processed_callback_fun) for split_name, loader in self.dataset_loaders.items()]

    def evaluate_dataset_split(self, model: NNModel, split_name: str,
                               dataset_loader: DatasetLoader, accelerator: Accelerator, epoch_result_callback_fun: Callable = None,
                               batch_processed_callback_fun: Callable = None) -> EvaluationBatchResult:
        """
        Evaulate torch NN Model on specific split of Data.

        :params:
               model (NNModel): Torch Neural Network module.
               split_name (str): Name of split of Dataset being evaluated.
               dataset_loader (DatasetLoader): Obhect of DatasetLoader used to load Data to be trained on.
               accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
               epoch_result_callback_fun (Callable): numner of batches to be trained.
               batch_processed_callback_fun (Callable): Batch number for which details to be logged.

        :returns:
            evaluation_result (EvaluationBatchResult): Evaluation results of batches trained on.
        """
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
        num_batches = len(dataset_loader)
        processed_batches = 0
        for batch in dataset_loader:
            inference_result_batch = self.forward_batch(dataset_batch=batch, model=model, postprocessors=post_processors)

            irb_filtered_dict = {"predictions": inference_result_batch.predictions, "targets": inference_result_batch.targets,
                                 "tags": inference_result_batch.tags}
            irb_filtered_dict_gathered = accelerator.gather_for_metrics(irb_filtered_dict)

            irb_filtered_gathered = InferenceResultBatch(predictions=irb_filtered_dict_gathered["predictions"],
                                                         targets=irb_filtered_dict_gathered["targets"],
                                                         tags=irb_filtered_dict_gathered["tags"])

            batch_loss = self._calculate_loss_scores(irb_filtered_gathered, split_loss_funs)
            batch_losses.append(batch_loss)

            irb_filtered = irb_filtered_gathered.split_results(predictions_keys=self.cpu_prediction_subscription_keys,
                                                               target_keys=self.cpu_target_subscription_keys,
                                                               device=torch.device("cpu"))

            inference_result_batches_cpu.append(irb_filtered)
            processed_batches += 1
            splits = list(self.dataset_loaders.keys())
            if accelerator.is_main_process:
                batch_processed_callback_fun(status="evaluation",
                                             num_batches=num_batches,
                                             current_batch=processed_batches,
                                             splits=splits,
                                             current_split=split_name)

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
        loss_scores = {key: [torch.mean(torch.Tensor([l[key] for l in batch_losses])).item()] for key in loss_keys}

        evaluation_result = EvaluationBatchResult(losses=loss_scores,
                                                  metrics=metric_scores,
                                                  dataset_name=dataset_loader.dataset_name,
                                                  split_name=split_name)
        if epoch_result_callback_fun is not None and accelerator.is_main_process:
            epoch_result_callback_fun(evaluation_result=evaluation_result)
        return evaluation_result

    def _get_metric_fun(self, identifier: str, target_subscription: Enum, prediction_subscription: Enum,
                        metric_fun: Callable, params: Dict[str, Any]) -> Metric:
        """
        Creating Metric object to be used for calcualting Metrics for the model.

        :params:
               identifier (str): Torch Neural Network module.
               target_subscription (Enum): Target Subscription key.
               prediction_subscription (Enum): Prediction Subscription key.
               metric_fun (Callable): Function to calculate Metric.
               params (Dict[str, Any]): Parameters for metric calcualtion.

        :returns:
            Metric object (Metric)
        """
        return Metric(identifier, target_subscription, prediction_subscription, metric_fun, params)

    def forward_batch(self, dataset_batch: DatasetBatch, model: NNModel,
                      postprocessors: List[PredictPostProcessingIF]) -> InferenceResultBatch:
        """
        NN Model predict on dataset batch.

        :params:
               dataset_batch (DatasetBatch): Train Dataset.
               model (NNModel): Torch Neural Network module.
               postprocessors (List[PredictPostProcessingIF]): TODO

        :returns:
            inference_result_batch (InferenceResultBatch): Prediction performed on the model.
        """
        inference_result_batch = self.inference_component.predict(model, dataset_batch, postprocessors)
        return inference_result_batch

    def _calculate_metric_scores(self, inference_batch: InferenceResultBatch, split_metrics: List[Metric]) -> Dict[str, List[float]]:
        """
        Calcualtion of metric scores on the splits of data set.

        :params:
               inference_batch (InferenceResultBatch): Prediction performed on the model.
               split_metrics (List[Metric]): Metrics for each split of data.
        :returns:
            metric_scores (Dict[str, List[float]]): Metric scores for splits.
        """
        metric_scores = {}
        for metric in split_metrics:
            try:
                metric_scores[metric.tag] = [metric(inference_batch)]
            except Exception as e:
                raise MetricCalculationError(f"Error during calculation of metric {metric.tag}") from e
        return metric_scores

    def _calculate_loss_scores(self, forward_batch: InferenceResultBatch, split_loss_funs: Dict[str, Loss]) -> Dict[str, List[float]]:
        """
        Calcualtion of loss scores on the splits of data set.

        :params:
               forward_batch (InferenceResultBatch): Prediction performed on the model.
               split_loss_funs (Dict[str, Loss]): Loss functions for splits.
        :returns:
            loss_scores (Dict[str, Loss]): Loss scores for splits.
        """
        loss_scores = {}
        for loss_key, loss_fun in split_loss_funs.items():
            try:
                loss_scores[loss_key] = self._get_batch_loss(loss_fun, forward_batch)
            except Exception as e:
                raise LossCalculationError("Error during calculation of loss {loss_key}") from e

        return loss_scores

    def _get_batch_loss(self, loss_fun: Loss, forward_batch: InferenceResultBatch) -> List[torch.Tensor]:
        """
        Evaulate torch NN Model on specific split of Data.

        :params:
               loss_fun (Loss): Loss function.
               forward_batch (InferenceResultBatch): Prediction performed on the model.
        :returns:
            loss (List[torch.Tensor]): Loss list for batch.
        """
        loss = loss_fun(forward_batch)
        loss = [loss.sum()]
        return loss
