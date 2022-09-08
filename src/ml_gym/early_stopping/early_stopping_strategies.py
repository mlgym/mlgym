from typing import List
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.error_handling.exception import BatchStateError


class EarlyStoppingIF:

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        raise NotImplementedError


class EarlyStopping(EarlyStoppingIF):
    def __init__(self, strategy: EarlyStoppingIF):
        self.strategy = strategy

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        return self.strategy.is_stopping_criterion_fulfilled(evaluation_results=evaluation_results, current_epoch=current_epoch)


class LastKEpochsImprovementStrategy(EarlyStoppingIF):

    def __init__(self, init_value: float, min_percentage_improvement: float, epochs_window: int, split_name: str, monitoring_key: str,
                 is_increase_task: bool):
        self.monitoring_values = [init_value]*epochs_window
        self.min_percentage_improvement = min_percentage_improvement
        self.epochs_window = epochs_window
        self.split_name = split_name
        self.monitoring_key = monitoring_key
        self.diff_filter_fun = min if is_increase_task else max

    def _get_monitoring_value(self, evaluation_results: List[EvaluationBatchResult]) -> float:
        evaluation_result = None
        for e in evaluation_results:
            if e.split_name == self.split_name:
                evaluation_result = e
                break
        try:
            value = evaluation_result.metrics[self.monitoring_key][-1] if self.monitoring_key in evaluation_result.metrics else evaluation_result.losses[self.monitoring_key][-1]
        except KeyError as e:
            raise BatchStateError(f"Monitoring key {self.monitoring_key} not present in metrics or losses.") from e
        return value

    def _evaluate_history(self, current_epoch: int) -> bool:
        def monitoring_diff_fun(i, current_epoch):
            return self.monitoring_values[(i + current_epoch) % self.epochs_window] - self.monitoring_values[(i-1 + current_epoch) % self.epochs_window]
        diffs = [monitoring_diff_fun(i, current_epoch) for i in range(self.epochs_window-1)]
        return abs(self.diff_filter_fun(diffs)) < self.min_percentage_improvement

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        monitoring_value = self._get_monitoring_value(evaluation_results)
        self.monitoring_values[current_epoch-1 % self.epochs_window] = monitoring_value

        perform_stop = self._evaluate_history(current_epoch)
        return perform_stop


class EarlyStoppingStrategyFactory:

    def get_last_k_epochs_improvement_strategy(init_value: float, min_percentage_improvement: float, epochs_window: int, split_name: str,
                                               monitoring_key: str, is_increase_task: bool) -> EarlyStoppingIF:
        strategy = LastKEpochsImprovementStrategy(init_value=init_value,
                                                  min_percentage_improvement=min_percentage_improvement,
                                                  epochs_window=epochs_window,
                                                  split_name=split_name,
                                                  monitoring_key=monitoring_key,
                                                  is_increase_task=is_increase_task)
        return EarlyStopping(strategy=strategy)
