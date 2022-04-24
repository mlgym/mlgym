from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from inspect import stack
from os import stat
from tracemalloc import start
import joblib
from ml_gym.gym.evaluator import EvaluationBatchResult
from typing import List, Dict
from dashify.logging.dashify_logging import ExperimentInfo
from ml_gym.persistency.io import DashifyWriter
from ml_gym.backend.streaming.client import ClientFactory, BufferedClient
import time


def get_timestamp() -> int:
    return int(time.time_ns()/1000)  # in ms


class MLgymStatusLoggerIF(ABC):

    @abstractmethod
    def log_job_status(self, job_id: int, job_type: str, status: str, model_id: str, starting_time: int, finishing_time: int, device: str,
                       error: str = "", stacktrace: str = ""):
        raise NotImplementedError

    @abstractmethod
    def log_model_status(self, model_id: str, status: str, current_epoch: int, splits: List[str], current_split: str, split_progress: int):
        raise NotImplementedError

    @abstractmethod
    def log_evaluation_results(self, eval_result: EvaluationBatchResult, epoch: int, model_id: str):
        raise NotImplementedError

    @abstractmethod
    def log_raw_message(self, raw_log_message: Dict):
        raise NotImplementedError


class LoggerCollection(MLgymStatusLoggerIF):

    def __init__(self, loggers: MLgymStatusLoggerIF):
        self._loggers = loggers

    def log_job_status(self, job_id: int, job_type: str, status: str, model_id: str, starting_time: int, finishing_time: int, device: str,
                       error: str = "", stacktrace: str = ""):
        for logger in self._loggers:
            logger.log_job_status(job_id, job_type, status, model_id, starting_time, finishing_time, device, error, stacktrace)

    def log_model_status(self, model_id: str, status: str, current_epoch: int, splits: List[str], current_split: str, split_progress: int):
        for logger in self._loggers:
            logger.log_model_status(model_id, status, current_epoch, splits, current_split, split_progress)

    def log_evaluation_results(self, eval_result: EvaluationBatchResult, epoch: int, model_id: str):
        for logger in self._loggers:
            logger.log_evaluation_results(eval_result, epoch, model_id)

    def log_raw_message(self, raw_log_message: Dict):
        for logger in self._loggers:
            logger.log_raw_message(raw_log_message)


class DiscLogger(MLgymStatusLoggerIF):
    def __init__(self):
        pass

    def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int, experiment_info: ExperimentInfo):
        DashifyWriter.log_measurement_result(results=results, experiment_info=experiment_info, measurement_id=epoch)

    def log_raw_message(self, raw_log_message: Dict):
        # TODO FIX experiment_info in interface
        DashifyWriter.log_raw_experiment_message(data_dict=raw_log_message, experiment_info=None)


class StreamedLogger(MLgymStatusLoggerIF):
    def __init__(self, host: str, port: int):
        self._sio_client: BufferedClient = ClientFactory.get_buffered_client(client_id="pool_event_publisher",
                                                                             host=host,
                                                                             port=port,
                                                                             disconnect_buffer_size=0)

    def log_job_status(self, job_id: int, job_type: str, status: str, model_id: str, starting_time: int, finishing_time: int, device: str,
                       error: str = "", stacktrace: str = ""):
        message = {"event_type": "evaluation_result", "creation_ts": get_timestamp()}
        payload = {"job_id": job_id, "job_typ": job_type, "status": status, "model_id": model_id, "starting_time": starting_time,
                   "finishing_time": finishing_time, "device": device, "error": error, "stacktrace": stacktrace}
        message["payload"] = payload
        self.log_raw_message(raw_log_message=message)

    def log_model_status(self, model_id: str, status: str, current_epoch: int, splits: List[str], current_split: str, split_progress: int):
        message = {"event_type": "evaluation_result", "creation_ts": get_timestamp()}
        payload = {"model_id": model_id, "status": status, "current_epoch": current_epoch,
                   "splits": splits, "current_split": current_split, "split_progress": split_progress}
        message["payload"] = payload
        self.log_raw_message(raw_log_message=message)

    def log_evaluation_results(self, eval_result: EvaluationBatchResult, epoch: int, model_id: str):
        message = {"event_type": "evaluation_result", "creation_ts": get_timestamp()}
        metric_scores = [{"metric": metric_key, "split": eval_result.split_name, "score": metric_score}
                         for metric_key, metric_score in eval_result.metrics.items()]
        loss_scores = [{"loss": loss_key, "split": eval_result.split_name, "score": loss_score}
                       for loss_key, loss_score in eval_result.losses.items()]
        payload = {"model_id": model_id, "epoch": epoch}
        payload["metric_scores"] = metric_scores
        payload["loss_scores"] = loss_scores
        message["payload"] = payload
        self.log_raw_message(raw_log_message=message)

    def log_raw_message(self, raw_log_message: Dict):
        self.sio_client.emit(message_key="mlgym_event", message=raw_log_message)


class MLgymStatusLoggerTypes(Enum):
    DISC_LOGGER = DiscLogger
    STREAMED_LOGGER = StreamedLogger


@dataclass
class MLgymStatusLoggerConfig:
    logger_type: MLgymStatusLoggerTypes
    logger_config: Dict


class LoggerConstructableIF:

    @abstractmethod
    def construct(self) -> MLgymStatusLoggerIF:
        raise NotImplementedError


@dataclass
class MLgymStatusLoggerConstructable(LoggerConstructableIF):
    config: MLgymStatusLoggerConfig

    def construct(self) -> MLgymStatusLoggerIF:
        return MLgymStatusLoggerTypes[self.config.logger_type](self.config.logger_config)


@dataclass
class MLgymStatusLoggerCollectionConstructable(LoggerConstructableIF):
    configs: List[MLgymStatusLoggerConfig]

    def construct(self) -> MLgymStatusLoggerIF:
        loggers = [MLgymStatusLoggerConstructable(config).construct() for config in self.configs]
        return LoggerCollection(loggers)
