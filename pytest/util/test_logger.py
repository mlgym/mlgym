import pytest
import tempfile
from ml_gym.util.logger import QueuedLogging, QLogger, LogLevel
from multiprocessing import Queue
import os
import time
from ml_gym import setup_logging_environment


class TestLogger:

    @pytest.fixture
    def tmp_folder_path(self) -> str:
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname

    @pytest.fixture
    def q_logger(self) -> str:
        return QueuedLogging.get_qlogger(logger_id="my_logger")

    def test_logging_with_local_queue(self, tmp_folder_path):
        test_message = "my test_message"
        logger_id = "my_logger"
        queue = Queue()
        q_logger = QLogger(logger_id, queue)
        QueuedLogging._instance = None
        QueuedLogging.start_logging(queue, tmp_folder_path)
        q_logger.log(LogLevel.DEBUG, test_message)
        log_file_path = os.path.join(tmp_folder_path, f"{logger_id}.log")
        QueuedLogging.stop_listener()
        # TODO this is really ugly
        time.sleep(5)
        with open(log_file_path, 'r') as fp:
            log_file_content = fp.read()
        assert test_message in log_file_content

    def test_logging_with_queued_logging_singleton(self, tmp_folder_path: str):
        test_message = "my test_message"
        logger_id = "my_logger"
        QueuedLogging._instance = None
        setup_logging_environment(tmp_folder_path)
        q_logger = QueuedLogging.get_qlogger(logger_id)
        q_logger.log(LogLevel.DEBUG, test_message)
        log_file_path = os.path.join(tmp_folder_path, f"{logger_id}.log")
        QueuedLogging.stop_listener()
        # TODO this is really ugly
        time.sleep(5)
        with open(log_file_path, 'r') as fp:
            log_file_content = fp.read()
        assert test_message in log_file_content
