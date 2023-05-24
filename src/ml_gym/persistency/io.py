from abc import abstractmethod
import base64
from dataclasses import dataclass
from enum import Enum
import pickle
from typing import Dict, List
from ml_gym.persistency.logging import ExperimentStatusLogger
import requests
from http import HTTPStatus
from ml_gym.error_handling.exception import NetworkError, DataIntegrityError
from abc import ABC
from ml_board.backend.restful_api.data_models import RawTextFile, FileFormat, ExperimentStatus, CheckpointResource


class GridSearchAPIClientIF(ABC):
    """
    GridSearchAPIClientIF class

    Contains the function definition of all HTTP calls to be made.
    """

    def get_config(self, grid_search_id: str, config_name: str):
        raise NotImplementedError

    def add_config_string(self, grid_search_id: str, config_name: str, config: Dict, experiment_id: int = None) -> Dict:
        raise NotImplementedError

    def get_validation_config(self, grid_search_id: str):
        raise NotImplementedError

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str, checkpoint_id: int, checkpoint_resource: CheckpointResource):
        raise NotImplementedError

    def add_checkpoint_resource(self, grid_search_id: str, experiment_id: str, payload: Dict):
        raise NotImplementedError

    def delete_checkpoints(self, grid_search_id: str, experiment_id: str, epoch: int):
        raise NotImplementedError

    def get_full_checkpoint(self, grid_search_id: str, experiment_id: str, checkpoint_id: int):
        raise NotImplementedError

    def get_unfinished_experiments(self, grid_search_id: str):
        raise NotImplementedError

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        raise NotImplementedError


class GridSearchRestfulAPIClient(GridSearchAPIClientIF):
    """
    GridSearchRestfulAPIClient class

    Contains the function implementation from GridSearchAPIClientIF for HTTP calls to be made.
    :params: GridSearchAPIClientIF
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def _get_json_resource(url) -> Dict:
        """
        ``HTTP GET Call`` Fetch json data.

        :params:
             endpoint (str): HTTP request URL

        :returns: bytes data
        """
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
        """
        ``HTTP GET Call`` Fetch bytes data.

        :params:
             url (str): HTTP request URL

        :returns: bytes data
        """
        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")
        else:
            return response.content

    def _post_binary_resource(url: str, payload: bytes) -> Dict:
        """
        ``HTTP POST Call`` Send bytes data.

        :params:
             url (str): HTTP request URL
             payload (bytes); pickle dump to be sent
        """
        data = base64.b64encode(payload)
        response = requests.post(
            url=url, data={"data": data, "msg": "insert checkpoint", "type": "multipart/form-data"}, files={"file": data}
        )
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")

    def _del_binary_resource(url: str) -> Dict:
        """
        ``HTTP DELETE Call`` Delete data.

        :params:
             url (str): HTTP request URL
        """
        response = requests.delete(url=url)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")

    def _put_raw_text_file_resource(url: str, payload: Dict) -> Dict:
        """
        ``HTTP PUT Call`` Send bytes data.

        :params:
             url (str): HTTP request URL
             payload (Dict); JSON object
        """
        response = requests.put(url=url, json=payload)
        if response.status_code != HTTPStatus.OK:
            raise NetworkError(f"Server responded with error code {response.status_code}")

    def get_config(self, grid_search_id: str, config_name: str) -> str:
        """
        ``HTTP GET Call`` Fetch json data.

        :params:
             grid_search_id (str): grid search ID
             config_name (str): file name to be fetched.

        :returns: bytes data
        """
        url = f"{self.endpoint}/{grid_search_id}/{config_name}"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    # def add_grid_search_config(self, grid_search_id: str, grid_search_config: Dict) -> Dict:
    #     url = f"{self.endpoint}/grid_searches/{grid_search_id}/gs_config"
    #     return GridSearchRestfulAPIClient._put_raw_text_file_resource(url, grid_search_config)

    def add_config_string(
        self, grid_search_id: str, config_name: str, config: str, file_format: FileFormat, experiment_id: int = None
    ) -> Dict:
        """
        ``HTTP PUT Call Request`` Add configuration
          given the grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             config_name (str): Name of Configuration file
             config (str): Config file
             file_format (FileFormat): Config file format
        """
        payload_dict = RawTextFile(file_format=file_format, content=config).dict()
        if experiment_id is None:
            url = f"{self.endpoint}/grid_searches/{grid_search_id}/{config_name}"
        else:
            url = f"{self.endpoint}/grid_searches/{grid_search_id}/{experiment_id}/{config_name}"

        return GridSearchRestfulAPIClient._put_raw_text_file_resource(url, payload_dict)

    def get_validation_config(self, grid_search_id: str):
        """
        ``HTTP GET Call Request`` Fetch validation
          given the grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID

        :returns: validation config json
        """
        url = f"{self.endpoint}/{grid_search_id}/validation_config"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_experiments(self, grid_search_id: str):
        """
        ``HTTP GET Call Request`` Fetch experiments
          given the grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID

        :returns: experiments json
        """
        url = f"{self.endpoint}/{grid_search_id}/experiments"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_full_checkpoint(self, grid_search_id: str, experiment_id: str, checkpoint_id: int):
        """
        ``HTTP GET Call Request`` Fetch full checkpoint
          given the grid search ID, experiment ID & checkpoint ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             checkpoint_id (int): Checkpoint ID

        :returns: checkpoint json
        """
        url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{checkpoint_id}"
        return GridSearchRestfulAPIClient._get_json_resource(url)

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str, checkpoint_id: int, checkpoint_resource: CheckpointResource):
        """
        ``HTTP GET Call Request`` Fetch checkpoint resource
          given the grid search ID, experiment ID & checkpoint ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             checkpoint_id (int): Checkpoint ID
             checkpoint_resource (CheckpointResource) : CheckpointResource type

        :returns: bytes pickel data
        """
        url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{checkpoint_id}/{checkpoint_resource}"
        return GridSearchRestfulAPIClient._get_binary_resource(url)

    def add_checkpoint_resource(self, grid_search_id: str, experiment_id: str, payload: Dict):
        """
        ``HTTP POST Call Request`` Send all checkpoint resource pickle files
          given the epoch, experiment ID & grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             payload (Dict): Dictionary containing CheckpointResource bytes array
        """

        chekpoint_resources = [
            CheckpointResource.model,
            CheckpointResource.lr_scheduler,
            CheckpointResource.optimizer,
            CheckpointResource.stateful_components,
        ]

        for checkpoint in chekpoint_resources:
            url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{payload['epoch']}/{checkpoint}"
            payload_pick = pickle.dumps(payload[f"{checkpoint}"])
            GridSearchRestfulAPIClient._post_binary_resource(url, payload_pick)

    def delete_checkpoints(self, grid_search_id: str, experiment_id: str, epoch: int):
        """
        ``HTTP DELETE Call Request`` Delete all checkpoint resource pickle files
          given the epoch, experiment ID & grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (int): Epoch
        """
        url = f"{self.endpoint}/checkpoints/{grid_search_id}/{experiment_id}/{epoch}"
        GridSearchRestfulAPIClient._del_binary_resource(url)

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        """
        ``HTTP GET Call Request`` Fetch Experiment status
          given the grid search ID over HTTP call.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (int): Epoch

        :returns: experiment status List
        """
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
