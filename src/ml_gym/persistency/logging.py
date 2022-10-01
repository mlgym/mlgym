from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Dict
from ml_gym.multiprocessing.states import JobStatus, JobType
from ml_gym.io.websocket_client import ClientFactory, BufferedClient
#from ml_gym.gym.model_checkpointing import ModelCheckpointComponent
import time
import torch
import pickle


def get_timestamp() -> int:
    return int(time.time_ns()/1000)  # in ms


class MLgymStatusLoggerIF(ABC):

    # @abstractmethod
    # def log_job_status(self, job_id: int, job_type: JobType, status: JobStatus, experiment_id: str, starting_time: int, finishing_time: int, device: torch.device,
    #                    error: str = "", stacktrace: str = ""):
    #     raise NotImplementedError

    # @abstractmethod
    # def log_model_status(self, experiment_id: str, status: str, current_epoch: int, splits: List[str], current_split: str, split_progress: int):
    #     raise NotImplementedError

    # @abstractmethod
    # def log_evaluation_results(self, eval_result: EvaluationBatchResult, epoch: int, experiment_id: str):
    #     raise NotImplementedError

    @abstractmethod
    def log_raw_message(self, raw_log_message: Dict):
        raise NotImplementedError


class LoggerCollection(MLgymStatusLoggerIF):

    def __init__(self, loggers: MLgymStatusLoggerIF):
        self._loggers = loggers

    # def log_job_status(self, job_id: int, job_type: JobType, status: JobStatus, experiment_id: str, starting_time: int, finishing_time: int, device: torch.device,
    #                    error: str = "", stacktrace: str = ""):
    #     for logger in self._loggers:
    #         logger.log_job_status(job_id, job_type, status, experiment_id, starting_time, finishing_time, device, error, stacktrace)

    # def log_model_status(self, experiment_id: str, status: str, current_epoch: int, splits: List[str], current_split: str, split_progress: int):
    #     for logger in self._loggers:
    #         logger.log_model_status(experiment_id, status, current_epoch, splits, current_split, split_progress)

    # def log_evaluation_results(self, eval_result: EvaluationBatchResult, epoch: int, experiment_id: str):
    #     for logger in self._loggers:
    #         logger.log_evaluation_results(eval_result, epoch, experiment_id)

    def log_raw_message(self, raw_log_message: Dict):
        for logger in self._loggers:
            logger.log_raw_message(raw_log_message)


class DiscLogger(MLgymStatusLoggerIF):
    def __init__(self):
        pass

    # # def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int, experiment_info: ExperimentInfo):
    # #     DashifyWriter.log_measurement_result(results=results, experiment_info=experiment_info, measurement_id=epoch)

    # def log_raw_message(self, raw_log_message: Dict):
    #     # TODO FIX experiment_info in interface
    #     DashifyWriter.log_raw_experiment_message(data_dict=raw_log_message, experiment_info=None)


class StreamedLogger(MLgymStatusLoggerIF):
    def __init__(self, host: str, port: int):
        self._sio_client: BufferedClient = ClientFactory.get_buffered_client(client_id="mlgym_streamed_logger",
                                                                             host=host,
                                                                             port=port,
                                                                             disconnect_buffer_size=0,
                                                                             rooms=["mlgym_event_publishers"])

    def log_raw_message(self, raw_log_message: Dict):
        self._sio_client.emit(message_key="mlgym_event", message=raw_log_message)


class JobStatusLogger:
    def __init__(self, logger: MLgymStatusLoggerIF) -> None:
        self._logger = logger

    def log_job_status(self, job_id: str, job_type: JobType, status: JobStatus, grid_search_id: str, experiment_id: str, starting_time: int, finishing_time: int,
                       device: torch.device, error: str = "", stacktrace: str = ""):
        message = {"event_type": "job_status", "creation_ts": get_timestamp()}
        payload = {"job_id": job_id, "job_type": job_type.value, "status": status.value, "grid_search_id": grid_search_id, "experiment_id": experiment_id,
                   "starting_time": starting_time, "finishing_time": finishing_time, "device": str(device), "error": error,
                   "stacktrace": stacktrace}
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)

    def log_experiment_config(self, grid_search_id: str, experiment_id: str, job_id: str, config: Dict[str, Any]):
        message = {"event_type": "experiment_config", "creation_ts": get_timestamp()}
        payload = {"grid_search_id": grid_search_id, "experiment_id": experiment_id, "job_id": job_id, "config": config}
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)


class ExperimentStatusLogger:
    def __init__(self, logger: MLgymStatusLoggerIF, experiment_id: str, grid_search_id: str) -> None:
        self._logger = logger
        self._grid_search_id = grid_search_id
        self._experiment_id = experiment_id

    def log_experiment_status(self, status: str, num_epochs: int, current_epoch: int, splits: List[str], current_split: str,
                              num_batches: int, current_batch: int):
        message = {"event_type": "experiment_status", "creation_ts": get_timestamp()}
        payload = {"grid_search_id": self._grid_search_id, "experiment_id": self._experiment_id, "status": status, "num_epochs": num_epochs, "current_epoch": current_epoch,
                   "splits": splits, "current_split": current_split, "num_batches": num_batches, "current_batch": current_batch}
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)

    def log_evaluation_results(self, eval_result: "EvaluationBatchResult", epoch: int):
        message = {"event_type": "evaluation_result", "creation_ts": get_timestamp()}
        metric_scores = [{"metric": metric_key, "split": eval_result.split_name, "score": metric_score[0]}
                         for metric_key, metric_score in eval_result.metrics.items()]
        loss_scores = [{"loss": loss_key, "split": eval_result.split_name, "score": loss_score[0]}
                       for loss_key, loss_score in eval_result.losses.items()]
        payload = {"grid_search_id": self._grid_search_id, "experiment_id": self._experiment_id, "epoch": epoch}
        payload["metric_scores"] = metric_scores
        payload["loss_scores"] = loss_scores
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)

    def log_checkpoint(self, epoch: int, model_binary_stream=None, optimizer_binary_stream=None, stateful_components_binary_stream=None):
        message = {"event_type": "checkpoint", "creation_ts": get_timestamp()}
        payload = {
            "grid_search_id": self._grid_search_id,
            "experiment_id": self._experiment_id,
            "checkpoint_id": epoch,
            "checkpoint_streams": {
                "model": pickle.dumps(model_binary_stream) if model_binary_stream is not None else None,
                "optimizer": pickle.dumps(optimizer_binary_stream) if optimizer_binary_stream is not None else None,
                "stateful_components": pickle.dumps(stateful_components_binary_stream) if stateful_components_binary_stream is not None else None
            }
        }
        message["payload"] = payload
        # for i in range(1000):
        self._logger.log_raw_message(raw_log_message=message)


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
        return self.config.logger_type.value(**self.config.logger_config)


@dataclass
class MLgymStatusLoggerCollectionConstructable(LoggerConstructableIF):
    configs: List[MLgymStatusLoggerConfig]

    def construct(self) -> MLgymStatusLoggerIF:
        loggers = [MLgymStatusLoggerConstructable(config).construct() for config in self.configs]
        return LoggerCollection(loggers)
