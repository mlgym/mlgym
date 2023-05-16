from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Dict
from ml_gym.multiprocessing.states import JobStatus, JobType
from ml_gym.io.websocket_client import ClientFactory, BufferedClient
import time
import torch
import io
import math


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

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError


class LoggerCollection(MLgymStatusLoggerIF):

    def __init__(self, loggers: List[MLgymStatusLoggerIF]):
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

    def disconnect(self):
        for logger in self._loggers:
            logger.disconnect()


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

    def disconnect(self):
        self._sio_client.disconnect()


class JobStatusLoggerIF(ABC):

    def log_job_status(self, job_id: str, job_type: JobType, status: JobStatus, grid_search_id: str, experiment_id: str, starting_time: int, finishing_time: int,
                       device: torch.device, error: str = "", stacktrace: str = ""):
        raise NotImplementedError

    def log_experiment_config(self, grid_search_id: str, experiment_id: str, job_id: str, config: Dict[str, Any]):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError


class JobStatusLogger(JobStatusLoggerIF):
    def __init__(self, logger: MLgymStatusLoggerIF) -> None:
        self._logger = logger

    def log_job_status(self, job_id: str, job_type: JobType, status: JobStatus, grid_search_id: str, experiment_id: str,
                       starting_time: int, finishing_time: int, error: str = "", stacktrace: str = ""):
        message = {"event_type": "job_status", "creation_ts": get_timestamp()}
        payload = {"job_id": job_id, "job_type": job_type.value, "status": status.value, "grid_search_id": grid_search_id,
                   "experiment_id": experiment_id, "starting_time": starting_time, "finishing_time": finishing_time, "error": error,
                   "stacktrace": stacktrace}
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)

    def log_experiment_config(self, grid_search_id: str, experiment_id: str, job_id: str, config: Dict[str, Any]):
        message = {"event_type": "experiment_config", "creation_ts": get_timestamp()}
        payload = {"grid_search_id": grid_search_id, "experiment_id": experiment_id, "job_id": job_id, "config": config}
        message["payload"] = payload
        self._logger.log_raw_message(raw_log_message=message)

    def disconnect(self):
        self._logger.disconnect()


class ExperimentStatusLogger:
    def __init__(self, logger: MLgymStatusLoggerIF, experiment_id: str, grid_search_id: str, binary_stream_chunk_size: int = 1000000):
        self._logger = logger
        self._grid_search_id = grid_search_id
        self._experiment_id = experiment_id
        self._binary_stream_chunk_size = binary_stream_chunk_size  # in bytes default 100,000 -> 100kb

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

    def log_checkpoint(self, epoch: int, model_state_dict=None, optimizer_state_dict=None, lr_scheduler_state_dict=None,
                       stateful_components_state_dict=None):
        def get_chunks(binary_stream, binary_stream_chunk_size: int):
            stream_length = len(binary_stream)
            num_chunks = math.ceil(stream_length/binary_stream_chunk_size)
            chunks = [binary_stream[i*binary_stream_chunk_size: (i+1)*binary_stream_chunk_size] for i in range(num_chunks)]
            return chunks

        data_dicts = {'model': model_state_dict,
                      'optimizer': optimizer_state_dict,
                      'lr_scheduler': lr_scheduler_state_dict,
                      'stateful_components': stateful_components_state_dict}
        data_streams = {}
        # Iterate over state dicts
        for key, state_dict in data_dicts.items():
            # If dict is not None call torch.save()
            if state_dict is not None:
                with io.BytesIO() as buffer:
                    torch.save(state_dict, buffer)
                    data_streams[key] = buffer.getvalue()
            else:
                data_streams[key] = None                

        for entity_id, binary_stream in data_streams.items():
            if binary_stream is not None:  # new checkpoint message
                print(f"Sending checkpoint entity {entity_id}")
                chunks = get_chunks(binary_stream, binary_stream_chunk_size=self._binary_stream_chunk_size)
                final_num_chunks = len(chunks)
                for chunk_id, chunk in enumerate(chunks):
                    payload = {
                        "grid_search_id": self._grid_search_id,
                        "experiment_id": self._experiment_id,
                        "checkpoint_id": epoch,
                        "entity_id": entity_id,
                        "chunk_data": chunk,
                        "chunk_id": chunk_id,
                        "final_num_chunks": final_num_chunks
                    }
                    message = {"event_type": "checkpoint", "creation_ts": get_timestamp()}
                    message["payload"] = payload
                    self._logger.log_raw_message(raw_log_message=message)

            else:  # delete message
                payload = {
                    "grid_search_id": self._grid_search_id,
                    "experiment_id": self._experiment_id,
                    "checkpoint_id": epoch,
                    "entity_id": entity_id,
                    "chunk_data": None,
                    "chunk_id": -1,
                    "final_num_chunks": 0
                }

                message = {"event_type": "checkpoint", "creation_ts": get_timestamp()}
                message["payload"] = payload
                self._logger.log_raw_message(raw_log_message=message)

    def disconnect(self):
        self._logger.disconnect()


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
