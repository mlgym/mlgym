import logging
import os
from multiprocessing import Queue, Process
from dataclasses import dataclass
import time
from abc import ABC, abstractmethod
from enum import Enum
import sys
import traceback
from ml_gym.error_handling.exception import SingletonAlreadyInstantiatedError


class LogLevel(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


@dataclass
class Message:
    logger_id: str
    message_string: str
    unix_timestamp: float
    level: LogLevel


class MLgymLoggerIF(ABC):

    def __init__(self, logger_id: str):
        self.logger_id = logger_id

    def build_message(self, level: LogLevel, message) -> Message:
        timestamp = time.time()
        message = Message(message_string=message, unix_timestamp=timestamp, level=level, logger_id=self.logger_id)
        return message

    @abstractmethod
    def log(self, level: LogLevel, message: str):
        raise NotImplementedError


class ConsoleLogger(MLgymLoggerIF):

    def __init__(self, logger_id: str):
        super().__init__(logger_id)
        self.logger = ConsoleLogger._get_console_logger(logger_id)

    def log(self, level: LogLevel, message: str):
        self.logger.log(level.value, message)

    @staticmethod
    def _get_console_logger(logger_id: str):
        # create / get logger
        logger = logging.getLogger(logger_id)
        # if logger has not been created
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)

            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(ch)
        return logger


class QLogger(MLgymLoggerIF):

    def __init__(self, logger_id: str, queue: Queue):
        super().__init__(logger_id)
        self.queue = queue

    def log(self, level: LogLevel, message: str):
        message = self.build_message(level, message)
        self.queue.put(message)


class QueuedLogging:
    _instance: "QueuedLogging" = None

    @classmethod
    def start_logging(cls, log_msg_queue: Queue, log_dir_path: str):
        if cls._instance is None:
            cls._instance = QueuedLogging(log_msg_queue, log_dir_path)
            cls._instance._start_listening()
        else:
            raise SingletonAlreadyInstantiatedError()

    @staticmethod
    def get_qlogger(logger_id: str) -> QLogger:
        return QLogger(logger_id, QueuedLogging._instance.log_msg_queue)

    def __init__(self, log_msg_queue: Queue, log_dir_path: str):
        if self._instance is not None:
            raise SingletonAlreadyInstantiatedError()
        self.log_msg_queue = log_msg_queue
        self.log_dir_path = log_dir_path
        self.listener_process = None

    def _start_listening(self):
        self.listener_process = Process(target=QueuedLogging._listener_process, args=(self.log_msg_queue, self.log_dir_path))
        self.listener_process.start()

    @staticmethod
    def stop_listener():
        QueuedLogging._instance.log_msg_queue.put_nowait(None)

    @staticmethod
    def _get_logger(log_dir_path: str, logger_id: str):
        logger = logging.getLogger(logger_id)
        log_file_path = os.path.join(log_dir_path, f"{logger_id}.log")
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    @staticmethod
    def _listener_process(queue: Queue, log_dir_path: str):
        loggers = {}
        while True:
            try:
                message: Message = queue.get()
                if message is None:  # We send this as a sentinel to tell the listener to quit.
                    break
                if message.logger_id not in loggers:
                    loggers[message.logger_id] = QueuedLogging._get_logger(log_dir_path, message.logger_id)
                loggers[message.logger_id].log(level=message.level.value, msg=message.message_string)
            except Exception:
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)


def get_console_logger(name: str):
    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    return logger
