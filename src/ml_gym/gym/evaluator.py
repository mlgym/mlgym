from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List
import torch
from ml_gym.batching.batch import DatasetBatch, EvaluationBatchResult, InferenceResultBatch
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.metrics.metrics import Metric
from ml_gym.models.nn.net import NNModel
from ml_gym.loss_functions.loss_functions import Loss, LossWarmupMixin
import tqdm
from ml_gym.util.logger import LogLevel, ConsoleLogger


class AbstractEvaluator(StatefulComponent):
    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError

    @abstractmethod
    def warm_up(self, model: NNModel, device: torch.device):
        raise NotImplementedError


class Evaluator(AbstractEvaluator):
    def __init__(self, eval_component: 'EvalComponentIF'):
        self.eval_component = eval_component

    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        return self.eval_component.evaluate(model, device)

    def warm_up(self, model: NNModel, device: torch.device):
        self.eval_component.warm_up(model, device)


class EvalComponentIF(StatefulComponent):
    @abstractmethod
    def warm_up(self, model: NNModel, device: torch.device):
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError


class EvalComponent(EvalComponentIF):
    """This thing always comes with batteries included, i.e., datasets, loss functions etc. are all already stored in here."""

    def __init__(self, inference_component: InferenceComponent, metrics: List[Metric],
                 loss_funs: Dict[str, Loss], dataset_loaders: Dict[str, DatasetLoader], train_split_name: str,
                 average_batch_loss: bool = True, show_progress: bool = False):
        self.loss_funs = loss_funs
        self.inference_component = inference_component
        self.metrics = metrics
        self.dataset_loaders = dataset_loaders
        self.average_batch_loss = average_batch_loss
        self.train_split_name = train_split_name
        self.show_progress = show_progress
        self.logger = ConsoleLogger("logger_eval_component")

    def warm_up(self, model: NNModel, device: torch.device):
        def init_loss_funs(batch: InferenceResultBatch):
            for _, loss_fun in self.loss_funs.items():
                if isinstance(loss_fun, LossWarmupMixin):
                    loss_fun.warm_up(batch)
                    loss_fun.finish_warmup()

        if any([isinstance(loss_fun, LossWarmupMixin) for _, loss_fun in self.loss_funs.items()]):
            self.logger.log(LogLevel.INFO, "Running warmup...")
            prediction_batches = self.map_batches(fun=self.forward_batch,
                                                  fun_params={"device": device, "model": model},
                                                  loader=self.dataset_loaders[self.train_split_name],
                                                  show_progress=self.show_progress)
            prediction_batch = InferenceResultBatch.combine(prediction_batches)
            init_loss_funs(prediction_batch)
        else:
            self.logger.log(LogLevel.INFO, "Skipping evaluation warmup. No special loss functions to be initialized.")

    def evaluate(self, model: NNModel, device: torch.device) -> List[EvaluationBatchResult]:
        return [self.evaluate_dataset_split(model, device, split_name, loader) for split_name, loader in self.dataset_loaders.items()]

    def evaluate_dataset_split(self, model: NNModel, device: torch.device, split_name: str, dataset_loader: DatasetLoader) -> EvaluationBatchResult:
        prediction_batches = self.map_batches(fun=self.forward_batch,
                                              loader=dataset_loader,
                                              fun_params={"device": device, "model": model},
                                              show_progress=self.show_progress)
        prediction_batch = InferenceResultBatch.combine(prediction_batches)
        loss_scores = self.calculate_loss_scores(prediction_batch)
        metric_scores = self.calculate_metric_scores(prediction_batch)
        evaluation_result = EvaluationBatchResult(losses=loss_scores,
                                                  metrics=metric_scores,
                                                  dataset_name=dataset_loader.dataset_name,
                                                  split_name=split_name)
        return evaluation_result

    @staticmethod
    def map_batches(fun: Callable[[DatasetBatch, Any], Any], loader: DatasetLoader,
                    fun_params: Dict[str, Any] = None, show_progress: bool = False) -> List[InferenceResultBatch]:
        """
        Applies a function to each batch within a DatasetLoader
        """
        fun_params = fun_params if fun_params is not None else dict()
        # TODO: This loads the entire dataset into memory.
        # We should make this a generator instead to prevent memory overflows.
        if show_progress:
            return [fun(batch, **fun_params) for batch in tqdm.tqdm(loader, desc="Batches processed:")]
        else:
            return [fun(batch, **fun_params) for batch in loader]
        return [fun(batch, **fun_params) for batch in loader]

    def _get_metric_fun(self, identifier: str, target_subscription: Enum, prediction_subscription: Enum,
                        metric_fun: Callable, params: Dict[str, Any]) -> Metric:
        return Metric(identifier, target_subscription, prediction_subscription, metric_fun, params)

    def forward_batch(self, batch: DatasetBatch, model: NNModel, device: torch.device) -> InferenceResultBatch:
        batch.to_device(device)
        model.to(device)
        with torch.no_grad():
            predict_result = self.inference_component.predict(model, batch)
        return predict_result

    def calculate_metric_scores(self, inference_batch: InferenceResultBatch) -> Dict[str, List[float]]:
        return {metric.tag: [metric(inference_batch)] for metric in self.metrics}

    def calculate_loss_scores(self, forward_batch: InferenceResultBatch) -> Dict[str, List[float]]:
        return {loss_key: self._get_batch_loss(loss_fun, forward_batch, self.average_batch_loss)
                for loss_key, loss_fun in self.loss_funs.items()}

    def _get_batch_loss(self, loss_fun: Loss, forward_batch: InferenceResultBatch, averaging: bool = True) -> List[float]:
        loss = loss_fun(forward_batch)
        if averaging:
            # TODO have to check if we actually need to do this since most loss funtions already average ...
            loss = [loss.detach().sum().item() / loss.shape[0]]
        else:
            loss = [loss.detach().tolist()]
        return loss
