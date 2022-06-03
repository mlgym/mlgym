from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.error_handling.exception import ExperimentInfoMissing
from ml_gym.persistency.io import DashifyReader, DashifyWriter


class StateLoggingCriterionStrategyIF(ABC):

    @abstractmethod
    def qualifies_for_logging(self, eval_results: List[EvaluationBatchResult]) -> bool:
        raise NotImplementedError


class LogAllCriterionStrategyImpl(StateLoggingCriterionStrategyIF):

    def qualifies_for_logging(self, eval_results: List[EvaluationBatchResult]) -> bool:
        return True


class StateLoggingIF(ABC):

    @abstractmethod
    def save_state(self, key: str, state_dict: Dict[str, Any], eval_results: List[EvaluationBatchResult],
                   experiment_info: ExperimentInfoMissing, epoch: int):
        raise NotImplementedError

    @abstractmethod
    def load_state(self, key: str, experiment_info: ExperimentInfoMissing, epoch: int) -> Dict[str, Any]:
        raise NotImplementedError


class StateLogging(StateLoggingIF):

    def __init__(self, state_logging_criterion_strategy: StateLoggingCriterionStrategyIF):
        self.state_logging_criterion_strategy = state_logging_criterion_strategy

    def save_state(self, key: str, state_dict: Dict[str, Any], eval_results: List[EvaluationBatchResult],
                   experiment_info: ExperimentInfoMissing, epoch: int):
        if self.state_logging_criterion_strategy.qualifies_for_logging(eval_results):
            DashifyWriter.save_binary_state(key, state_dict, experiment_info, epoch)

    def load_state(self, key: str, experiment_info: ExperimentInfoMissing, epoch: int) -> Dict[str, Any]:
        state_dict = DashifyReader.load_state(key=key, experiment_info=experiment_info,
                                              measurement_id=epoch)
        return state_dict
