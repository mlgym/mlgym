from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import requests
from http import HTTPStatus
from ml_gym.error_handling.exception import NetworkError, DataIntegrityError
from abc import ABC
from ml_board.backend.restful_api.data_models import RawTextFile, FileFormat, ExperimentStatus, CheckpointResource


class GridSearchAPIClientIF(ABC):

    def get_config(self, grid_search_id: str, config_name: str):
        raise NotImplementedError

    def add_config_string(self, grid_search_id: str, config_name: str, config: Dict, experiment_id: int = None) -> Dict:
        raise NotImplementedError

    def get_validation_config(self, grid_search_id: str):
        raise NotImplementedError

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int,
                                checkpoint_resource: CheckpointResource):
        raise NotImplementedError

    def get_full_checkpoint(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int):
        raise NotImplementedError

    def get_unfinished_experiments(self, grid_search_id: str):
        raise NotImplementedError

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        raise NotImplementedError


class GridSearchRestfulAPIClient(GridSearchAPIClientIF):

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def _get_json_resource(url) -> Dict:
        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")
        else:
            try:
                grid_search_config = response.json()
            except ValueError as e:
                raise DataIntegrityError(f"Could not cast response from {url} to json.") from e
            return grid_search_config

    def _get_binary_resource(url) -> bytes:
        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")
        else:
            return response.content

    def _set_raw_text_file_resource(url: str, payload: Dict) -> Dict:
        response = requests.put(url=url, json=payload)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")

    def get_config(self, grid_search_id: str, config_name: str) -> str:
        url = f"{self.endpoint}/{grid_search_id}/{config_name}"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    # def add_grid_search_config(self, grid_search_id: str, grid_search_config: Dict) -> Dict:
    #     url = f"{self.endpoint}/grid_searches/{grid_search_id}/gs_config"
    #     return GridSearchRestfulAPIClient._set_raw_text_file_resource(url, grid_search_config)

    def add_config_string(self, grid_search_id: str, config_name: str, config: str, file_format: FileFormat,
                          experiment_id: int = None) -> Dict:
        payload_dict = RawTextFile(file_format=file_format, content=config).dict()
        if experiment_id is None:
            url = f"{self.endpoint}/grid_searches/{grid_search_id}/{config_name}"
        else:
            url = f"{self.endpoint}/grid_searches/{grid_search_id}/{experiment_id}/{config_name}"

        return GridSearchRestfulAPIClient._set_raw_text_file_resource(url, payload_dict)

    def get_validation_config(self, grid_search_id: str):
        url = f"{self.endpoint}/{grid_search_id}/validation_config"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_experiments(self, grid_search_id: str):
        url = f"{self.endpoint}/{grid_search_id}/experiments"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_full_checkpoint(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int):
        url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{checkpoint_id}"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str,  checkpoint_id: int,
                                checkpoint_resource: CheckpointResource):
        url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{checkpoint_id}/{checkpoint_resource}"
        return GridSearchRestfulAPIClient._get_binary_resource(url)

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        url = f"{self.endpoint}/grid_searches/{grid_search_id}/experiments"
        response = GridSearchRestfulAPIClient._get_json_resource(url)
        experiment_statuses = [ExperimentStatus(**r) for r in response]
        return experiment_statuses


class GridSearchAPIClientConstructableIF(ABC):

    @abstractmethod
    def construct(self) -> GridSearchAPIClientIF:
        raise NotImplementedError


class GridSearchAPIClientType(Enum):
    GRID_SEARCH_RESTFUL_API_CLIENT = GridSearchRestfulAPIClient


@dataclass
class GridSearchAPIClientConfig:
    api_client_type: GridSearchAPIClientType
    api_client_config: Dict


@dataclass
class GridSearchAPIClientConstructable(GridSearchAPIClientConstructableIF):
    config: GridSearchAPIClientConfig

    def construct(self) -> GridSearchAPIClientIF:
        return self.config.api_client_type.value(**self.config.api_client_config)
