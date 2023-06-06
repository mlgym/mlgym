from typing import Any, List, Dict
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.error_handling.exception import BatchStateError
from ml_gym.gym.stateful_components import StatefulComponent
import numpy as np


class EarlyStoppingIF(StatefulComponent):
    """
    Early Stopping Interface containing function to cehck for stopping criteria.
    """

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        raise NotImplementedError


class EarlyStopping(EarlyStoppingIF):
    """
    Early Stopping Stratergy Class containing functions for performing early stopping.
    """
    def __init__(self, strategy: EarlyStoppingIF):
        self.strategy = strategy

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        return self.strategy.is_stopping_criterion_fulfilled(evaluation_results=evaluation_results, current_epoch=current_epoch)

    def get_state(self) -> Dict[str, Any]:
        state = self.strategy.get_state()
        return state

    def set_state(self, state: Dict[str, Any]):
        self.strategy.set_state(state)


class LastKEpochsImprovementStrategy(EarlyStoppingIF):
    """
    Class containing functions to perform last K epochs Improvement Early Stopping Stratergy.
    """

    def __init__(self, min_relative_improvement: float, epochs_window: int, split_name: str, monitoring_key: str,
                 is_increase_task: bool):
        monitoring_values_list = [1]
        init_min_relative_improvement = min_relative_improvement * 1.1  # we need to make this a bit bigger for precision inaccuracies
        for i in range(1, epochs_window):
            monitoring_values_list.append(monitoring_values_list[i-1] + monitoring_values_list[i-1]*init_min_relative_improvement)
        self.monitoring_values = np.array(monitoring_values_list)
        if not is_increase_task:
            self.monitoring_values = self.monitoring_values[::-1]
        self.min_relative_improvement = min_relative_improvement
        self.epochs_window = epochs_window
        self.split_name = split_name
        self.monitoring_key = monitoring_key
        self.is_increase_task = is_increase_task

    def _get_monitoring_value(self, evaluation_results: List[EvaluationBatchResult]) -> float:
        """
        Get values from the key which are being monitored

        :params:
            evaluation_results (List[EvaluationBatchResult]): Object storing entire evaluation infotmation.
        :returns:
            value (float): value of the monitored key.
        """
        evaluation_result = None
        for e in evaluation_results:
            if e.split_name == self.split_name:
                evaluation_result = e
                break
        if evaluation_result is None:
            raise BatchStateError(f"EvaluationBatchResults do not contain split_name {self.split_name}. Check the configuration file. ")
        try:
            value = evaluation_result.metrics[self.monitoring_key][-1] if self.monitoring_key in evaluation_result.metrics else evaluation_result.losses[self.monitoring_key][-1]
        except KeyError as e:
            raise BatchStateError(f"Monitoring key {self.monitoring_key} not present in metrics or losses.") from e
        return value

    def _evaluate_history(self, current_epoch: int) -> bool:
        """
        Evaluate history for last K epochs Improvement.

        :params:
            current_epoch (int): Current epoch number.
        :returns:
            (bool): True or False boolean response if condition is met or not met.
        """
        def monitoring_diff_fun(i, current_epoch):
            next_val = self.monitoring_values[(i + 2 + current_epoch) % self.epochs_window]
            base_val = self.monitoring_values[(i + 1 + current_epoch) % self.epochs_window]
            relative_diff = (next_val - base_val) / base_val
            return relative_diff

        relative_diffs = [monitoring_diff_fun(i, current_epoch) for i in range(self.epochs_window-1)]
        if self.is_increase_task:
            return max(relative_diffs) < self.min_relative_improvement
        else:
            return min(relative_diffs) > self.min_relative_improvement * -1

    def is_stopping_criterion_fulfilled(self, evaluation_results: List[EvaluationBatchResult], current_epoch: int) -> bool:
        """
        Check if the stopping criteria has been fulfilled.

        :params:
                evaluation_results (List[EvaluationBatchResult]): Object storing entire evaluation infotmation.
                current_epoch (int): Current epoch number.

        :returns:
            perform_stop (bool): True or False boolean response if condition is met or not met for early stopping.
        """
        monitoring_value = self._get_monitoring_value(evaluation_results)
        self.monitoring_values[current_epoch % self.epochs_window] = monitoring_value

        perform_stop = self._evaluate_history(current_epoch)
        return perform_stop

    def get_state(self) -> Dict[str, Any]:
        state = {"monitoring_values": self.monitoring_values.tolist()}
        return state

    def set_state(self, state: Dict[str, Any]):
        self.monitoring_values = np.array(state["monitoring_values"])


class EarlyStoppingStrategyFactory:
    """
    Factory containing all possible early stopping stratergies.
    """

    def get_last_k_epochs_improvement_strategy(min_relative_improvement: float, epochs_window: int, split_name: str,
                                               monitoring_key: str, is_increase_task: bool) -> EarlyStoppingIF:
        """
        Perform last K epochs Improvement Early Stopping Stratergy.

        :params:
                min_relative_improvement (float): value for minimum relative improvement between epochs to be checked.
                epoch_window (int): Epochs to be monitored.
                split_name (str): Name of the split.
                monitoring_key (str): Key of the metric to be monitored.
                is_increase_task (bool): Is the task to be monitored an increase or decrease task.
            
        :returns:
            EarlyStoppingIF object: Initialzied with LastKEpochsImprovementStrategy.
        """
        strategy = LastKEpochsImprovementStrategy(min_relative_improvement=min_relative_improvement,
                                                  epochs_window=epochs_window,
                                                  split_name=split_name,
                                                  monitoring_key=monitoring_key,
                                                  is_increase_task=is_increase_task)
        return EarlyStopping(strategy=strategy)
