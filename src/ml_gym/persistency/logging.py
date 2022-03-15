from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from ml_gym.blueprints.constructables import ComponentConstructable
from ml_gym.gym.evaluator import EvaluationBatchResult
from typing import List, Dict
from dashify.logging.dashify_logging import ExperimentInfo
from ml_gym.persistency.io import DashifyWriter
from ml_gym.backend.streaming.client import ClientFactory, BufferedClient


class MLgymStatusLoggerIF(ABC):

    @abstractmethod
    def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int):
        raise NotImplementedError

    @abstractmethod
    def log_raw_message(self, raw_log_message: Dict):
        raise NotImplementedError


class LoggingCollection(MLgymStatusLoggerIF):

    def __init__(self, loggers: MLgymStatusLoggerIF):
        self._loggers = loggers

    def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int):
        for logger in self._loggers:
            logger.log_evaluation_results(results, epoch)

    def log_raw_message(self, raw_log_message: Dict):
        for logger in self._loggers:
            logger.log_raw_message(raw_log_message)


class DiscLogger(MLgymStatusLoggerIF):
    def __init__(self, experiment_info: ExperimentInfo):
        self._experiment_info = experiment_info

    def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int):
        DashifyWriter.log_measurement_result(results=results, experiment_info=self._experiment_info, measurement_id=epoch)

    def log_raw_message(self, raw_log_message: Dict):
        DashifyWriter.log_raw_experiment_message(data_dict=raw_log_message, experiment_info=self._experiment_info)


class StreamedLogger(MLgymStatusLoggerIF):
    def __init__(self, host: str, port: int, experiment_info: ExperimentInfo):
        self._experiment_info = experiment_info
        self._sio_client: BufferedClient = ClientFactory.get_buffered_client(client_id="pool_event_publisher",
                                                                             host=host,
                                                                             port=port,
                                                                             disconnect_buffer_size=0)

    def log_evaluation_results(self, results: List[EvaluationBatchResult], epoch: int):
        DashifyWriter.log_measurement_result(results=results, experiment_info=self._experiment_info, measurement_id=epoch)

    def log_raw_message(self, raw_log_message: Dict):
        self.sio_client.emit(message_key="mlgym_event", message=raw_log_message)


class MLgymStatusLoggerTypes(Enum):
    DISC_LOGGER = DiscLogger


@dataclass
class MLgymStatusLoggerConfig:
    logger_type: MLgymStatusLoggerTypes
    logger_config: Dict


@dataclass
class MLgymStatusLoggerConstructable:
    config: MLgymStatusLoggerConfig

    def _construct_impl(self) -> MLgymStatusLoggerIF:
        return MLgymStatusLoggerTypes[self.config.logger_type](self.config.logger_config)
