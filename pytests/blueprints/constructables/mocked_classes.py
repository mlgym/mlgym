from data_stack.dataset.iterator import DatasetIteratorIF
from data_stack.dataset.iterator import SequenceDatasetIterator
from data_stack.dataset.factory import BaseDatasetFactory
import torch
import random
from data_stack.dataset.meta import IteratorMeta
from typing import Tuple, Dict, Any, List

from ml_gym.data_handling.postprocessors.collator import Collator
from ml_gym.models.nn.net import NNModel
from ml_gym.multiprocessing.states import JobStatus, JobType
from ml_gym.persistency.logging import JobStatusLoggerIF, MLgymStatusLoggerIF
from ml_gym.persistency.io import GridSearchAPIClientIF
from abc import ABC
from ml_board.backend.restful_api.data_models import ExperimentStatus, CheckpointResource


class MockedMNISTIterator(SequenceDatasetIterator):

    def __init__(self, num_samples: int = 500):
        targets = [random.randint(0, 9) for _ in range(num_samples)]
        samples = torch.rand(num_samples, 28, 28)
        dataset_sequences = [samples, targets, targets]
        super().__init__(dataset_sequences=dataset_sequences)


class MockedMNISTFactory(BaseDatasetFactory):
    def __init__(self):
        super().__init__(storage_connector=None)

    def get_dataset_iterator(self, config: Dict[str, Any] = None) -> Tuple[DatasetIteratorIF, IteratorMeta]:
        return MockedMNISTIterator(), IteratorMeta(sample_pos=0, target_pos=1, tag_pos=2)


class MockedCollator(Collator):
    target_publication_key: str = None

    def __call__(self, batch: List[torch.Tensor]):
        pass


class MockedNNModel(NNModel):
    def __init__(self, seed, layer_config: Dict = None, prediction_publication_key: str = None):
        super().__init__(seed=seed)
        self.prediction_publication_key = prediction_publication_key

    def forward_impl(self, inputs: torch.Tensor):
        pass


class ConstructableIF(ABC):

    def construct():
        raise NotImplementedError


class MockedMLgymStatusLogger(MLgymStatusLoggerIF, ConstructableIF):

    def log_raw_message(self, raw_log_message: Dict):
        return

    def construct():
        return MockedMLgymStatusLogger()


class MockedJobStatusLogger(JobStatusLoggerIF, ConstructableIF):

    def log_job_status(self, job_id: str, job_type: JobType, status: JobStatus, grid_search_id: str, experiment_id: str, starting_time: int, finishing_time: int,
                       device: torch.device, error: str = "", stacktrace: str = ""):
        return

    def log_experiment_config(self, grid_search_id: str, experiment_id: str, job_id: str, config: Dict[str, Any]):
        return

    def construct():
        return MockedJobStatusLogger()


class MockedGridSearchAPIClient(GridSearchAPIClientIF, ConstructableIF):

    def get_config(self, grid_search_id: str, config_name: str):
        return

    def add_config_string(self, grid_search_id: str, config_name: str, config: Dict, experiment_id: int = None) -> Dict:
        return

    def get_validation_config(self, grid_search_id: str):
        return

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int,
                                checkpoint_resource: CheckpointResource):
        return

    def get_full_checkpoint(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int):
        return

    def get_unfinished_experiments(self, grid_search_id: str):
        return

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        return

    def construct():
        return MockedGridSearchAPIClient()
