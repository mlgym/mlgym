from abc import ABC, abstractmethod
from io import BytesIO
import os
import glob
import re
import shutil
from typing import Dict, List
from fastapi import UploadFile
from ml_gym.error_handling.exception import InvalidPathError, ModelCardFetchError
import json
from ml_board.backend.restful_api.data_models import FileFormat, RawTextFile, CheckpointResource, ExperimentStatus
from ml_gym.models.nn.net import NNModel
from ml_gym.util.util import ModelCardFactory
from pyparsing import Generator
import torch
import yaml
from pathlib import Path
import json


class DataAccessIF(ABC):
    """
    DataAccessIF class
    Declare Abstract methods to be used in FileDataAccess Class.
    """

    @abstractmethod
    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        raise NotImplementedError

    @abstractmethod
    def add_raw_config_to_grid_search(self, grid_search_id: str, config_name: str, config_file: RawTextFile) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_config_to_experiment(self, grid_search_id: str, experiment_id: str, config_name: str, config: RawTextFile) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_grid_config(self, grid_search_id: str, config_name: str) -> Generator:
        raise NotImplementedError

    @abstractmethod
    def get_experiment_config(self, grid_search_id: str, experiment_id: str, config_name: str) -> Generator:
        raise NotImplementedError

    @abstractmethod
    def load_config(self, grid_search_id: str, experiment_id: str, config_name: str, file_type: str) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def get_checkpoint_list(self, grid_search_id: str, experiment_id: str) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def get_checkpoint_resource(self, grid_search_id: str, epoch: str, checkpoint_resource: str, experiment_id: str = None) -> BytesIO | Generator:
        raise NotImplementedError

    @abstractmethod
    def add_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_file: UploadFile) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_checkpoints(self, grid_search_id: str, experiment_id: str, epoch: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_checkpoint_dict_epoch(self, grid_search_id: str, experiment_id: str, epoch: str) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def create_model_card(self, grid_search_id: str, experiment_id: str) -> Dict:
        raise NotImplementedError


class FileDataAccess(DataAccessIF):
    """
    FileDataAccess Class
    :params:
        DataAccessIF object

    The rest server uses this class to use methods to access event storage files.
    Used to add new files, delete current files and fetch current files.
    """

    def __init__(self, top_level_logging_path: str):
        print(top_level_logging_path)
        self.top_level_logging_path = top_level_logging_path

    @staticmethod
    def is_safe_path(base_dir, requested_path, follow_symlinks=True):
        # resolves symbolic links
        if follow_symlinks:
            matchpath = os.path.realpath(requested_path)
        else:
            matchpath = os.path.abspath(requested_path)
        return base_dir == os.path.commonpath((base_dir, matchpath))

    @staticmethod
    def get_checkpoint_files(path: str, base_path: str):
        full_paths = glob.glob(os.path.join(path, "**", "*.pickle"), recursive=True)
        return sorted([os.path.relpath(full_path, base_path) for full_path in full_paths], reverse=True)

    @staticmethod
    def iterfile(file_path: str):
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    @staticmethod
    def iterbytefile(file_path: str):
        with open(file_path, mode="rb") as f:
            buffer = BytesIO(f.read())
        return buffer

    def get_experiment_statuses(self, grid_search_id: str) -> List[ExperimentStatus]:
        """
        Fetch experiment status for a Grid Search ID.
        :params:
             grid_search_id (str): Grid Search ID
        :returns: List     experiment_statuses
        """

        def get_last_checkpoint_ids(top_level_logging_path: str, grid_search_id: str) -> Dict:
            paths = glob.glob(os.path.join(top_level_logging_path, grid_search_id, "**/*"), recursive=True)
            regex_checkpoints = r".*-\d\d\/(\d)\/(\d)$"
            regex_experiments = r".*-\d\d\/(\d)$"

            experiment_id_to_checkpoint_ids = {}
            for path in paths:
                # experiment match
                match = re.match(regex_experiments, path)
                if match is not None:
                    experiment_id = int(match.groups()[0])
                    if experiment_id not in experiment_id_to_checkpoint_ids:
                        experiment_id_to_checkpoint_ids[experiment_id] = [-1]

                # checkpoint match
                match = re.match(regex_checkpoints, path)
                if match is not None:
                    experiment_id, checkpoint_id = int(match.groups()[0]), int(match.groups()[1])
                    if experiment_id not in experiment_id_to_checkpoint_ids:
                        experiment_id_to_checkpoint_ids[experiment_id] = []
                    experiment_id_to_checkpoint_ids[experiment_id].append(checkpoint_id)
            epxeriment_id_to_last_checkpoint = {k: max(v) for k, v in experiment_id_to_checkpoint_ids.items()}
            return epxeriment_id_to_last_checkpoint

        def load_experiment_config(top_level_logging_path: str, grid_search_id: str, experiment_id: int) -> Dict:
            full_path = os.path.join(top_level_logging_path, grid_search_id, str(experiment_id), "experiment_config.json")
            with open(full_path, "r") as fp:
                experiment_config = json.load(fp)
            return experiment_config

        requested_full_path = os.path.realpath(os.path.join(self.top_level_logging_path, grid_search_id))

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            epxeriment_id_to_last_checkpoint_id = get_last_checkpoint_ids(self.top_level_logging_path, grid_search_id)
            response = [
                ExperimentStatus(
                    **{
                        "experiment_id": experiment_id,
                        "last_checkpoint_id": last_checkpoint_id,
                        "experiment_config": load_experiment_config(self.top_level_logging_path, grid_search_id, experiment_id),
                    }
                )
                for experiment_id, last_checkpoint_id in epxeriment_id_to_last_checkpoint_id.items()
            ]
            return response

        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def add_raw_config_to_grid_search(self, grid_search_id: str, config_name: str, config_file: RawTextFile) -> None:
        """
        Add Config for a Grid Search ID to event storage

        :params:
                grid_search_id (str): Grid Search ID
                config_name (str): Name of Configuration file
                config_file (RawTextFile) : RawTextFile Object
        """
        requested_full_path = os.path.realpath(os.path.join(self.top_level_logging_path, str(grid_search_id), config_name))

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            os.makedirs(os.path.dirname(requested_full_path), exist_ok=True)
            with open(requested_full_path, "w") as fp:
                fp.writelines(config_file.content)
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def add_config_to_experiment(self, grid_search_id: str, experiment_id: str, config_name: str, config: RawTextFile) -> None:
        """
        Add experiment config given the experiment ID & grid search ID to event storage.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                config_name (str): Name of Configuration file
                config (RawTextFile) : RawTextFile Object
        """
        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), config_name)
        )

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            os.makedirs(os.path.dirname(requested_full_path), exist_ok=True)
            with open(requested_full_path, "w") as fp:
                fp.writelines(config.content)

        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def get_grid_config(self, grid_search_id: str, config_name: str) -> Generator:
        """
        Fetch grid config for a Grid Search ID from the event storage.

        :params:
                grid_search_id (str): Grid Search ID
                config_name (str): Name of Configuration file

        :returns: bytes response of YML file
        """
        requested_full_path = os.path.realpath(os.path.join(self.top_level_logging_path, str(grid_search_id), f"{config_name}.yml"))
        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            if not os.path.isfile(requested_full_path):
                raise InvalidPathError(f"Resource {requested_full_path} not found.")

            generator = FileDataAccess.iterfile(requested_full_path)
            return generator
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def get_experiment_config(self, grid_search_id: str, experiment_id: str, config_name: str) -> Generator:
        """
        Fetch experiment config given the experiment ID & grid search ID from event storage.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                config_name (str): Name of Configuration file

        :returns: bytes response of JSON file
        """
        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), f"{config_name}.json")
        )
        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            if not os.path.isfile(requested_full_path):
                raise InvalidPathError(f"Resource {requested_full_path} not found.")

            generator = FileDataAccess.iterfile(requested_full_path)
            return generator
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def load_config(self, grid_search_id: str, config_name: str, file_type: str, experiment_id: str = None) -> Dict:
        """
        Load config to be used in backend buisness logic.

        :params:
                grid_search_id (str): Grid Search ID
                config_name (str): Name of Configuration file
                file_type (str): Type of configuration file to be loaded ('json' or 'yaml)
                experiment_id (str): Experiment ID

        :returns: YML or JSON file
        """
        if experiment_id is not None:
            requested_full_path = os.path.realpath(
                os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), f"{config_name}.{file_type}")
            )
        else:
            requested_full_path = os.path.realpath(
                os.path.join(self.top_level_logging_path, str(grid_search_id), f"{config_name}.{file_type}")
            )
        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            if not os.path.isfile(requested_full_path):
                raise InvalidPathError(f"Resource {requested_full_path} not found.")

            if file_type == "yml":
                data = yaml.safe_load(Path(requested_full_path).read_text())
            else:
                data = json.loads(Path(requested_full_path).read_text())
            return data
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def get_checkpoint_dict_epoch(self, grid_search_id: str, experiment_id: str, epoch: str) -> List[Dict]:
        """
        Fetch all checkpoint resource pickle file names from event storage
        given the epoch, experiment ID & grid search ID.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                epoch (str): Epoch number

        :returns: List of Checkpoint file names in an epoch
        """
        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch))
        )

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            response = []
            checkpoints = []
            files = FileDataAccess.get_checkpoint_files(requested_full_path, base_path=self.top_level_logging_path)
            for file_num in range(len(files)):
                split = os.path.normpath(files[file_num]).split(os.sep)
                checkpoints.append(os.path.basename(split[-1]))
            response.append({"experiment_id": experiment_id, "epoch": epoch, "checkpoints": checkpoints})
            return response

        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def get_checkpoint_list(self, grid_search_id: str, experiment_id) -> List[Dict]:
        """
        Fetch all checkpoint resource pickle file names given the experiment ID & grid search ID from event storage.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID

        :returns: List of Checkpoint file names in an experiment
        """
        requested_full_path = os.path.realpath(os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id)))

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            response = []
            checkpoints = []
            files = FileDataAccess.get_checkpoint_files(requested_full_path, base_path=self.top_level_logging_path)
            last_epoch = os.path.normpath(files[0]).split(os.sep)[-2]
            for file_num in range(len(files)):
                split = os.path.normpath(files[file_num]).split(os.sep)
                epoch = split[-2]
                if epoch != last_epoch:
                    response.append({"experiment_id": experiment_id, "epoch": last_epoch, "checkpoints": checkpoints})
                    last_epoch = epoch
                    checkpoints = []
                    checkpoints.append(os.path.basename(split[-1]))
                else:
                    checkpoints.append(os.path.basename(split[-1]))

            response.append({"experiment_id": experiment_id, "epoch": epoch, "checkpoints": checkpoints})
            return response

        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: str) -> BytesIO | Generator:
        """
        Fetch checkpoint resource pickle file given the experiment ID & grid search ID from event storage.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                epoch (str): Epoch number
                checkpoint_resource (CheckpointResource) : CheckpointResource type

        :returns: bytes response of pickle file
        """
        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch), checkpoint_resource)
        )
        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            if not os.path.isfile(requested_full_path):
                raise InvalidPathError(f"Resource {requested_full_path} not found.")

            if checkpoint_resource is not CheckpointResource.stateful_components:
                data = FileDataAccess.iterbytefile(requested_full_path)
            else:
                data = FileDataAccess.iterfile(requested_full_path)
            return data
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def add_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_file: UploadFile) -> None:
        """
        Add a checkpoint resource pickle file given the epoch, experiment ID & grid search ID to event storage.

        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                epoch (str): Epoch number
                checkpoint_resource (CheckpointResource) : CheckpointResource type
                payload_pickle (bytes): Pickle file to be added

        :returns: Pickle file Stream response
        """
        file_name = checkpoint_file.filename
        file_path = os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch), file_name)
        requested_full_path = os.path.realpath(file_path)

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            os.makedirs(os.path.dirname(requested_full_path), exist_ok=True)
            with open(requested_full_path, "wb") as fd:
                shutil.copyfileobj(checkpoint_file.file, fd)
        else:
            raise InvalidPathError(f"File path {requested_full_path} is not safe.")

    def delete_checkpoints(self, grid_search_id: str, experiment_id: str, epoch: str) -> None:
        """
        Delete checkpoint FOLDER From the event storage
        given the epoch, experiment ID & grid search ID.
        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                epoch (str): Epoch number
        """

        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch))
        )

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            shutil.rmtree(requested_full_path)
        else:
            raise InvalidPathError(f"The path {requested_full_path} is not safe.")

    def delete_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: str) -> None:
        """
        Delete checkpoint resource pickle file from the event storage
        given the epoch, experiment ID & grid search ID.
        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID
                epoch (str): Epoch number
                checkpoint_resource (CheckpointResource) : CheckpointResource type
        """

        folder_path = os.path.realpath(os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch)))
        requested_full_path = os.path.realpath(
            os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch), checkpoint_resource)
        )

        if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
            os.remove(requested_full_path)
            if len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))]) == 0:
                os.rmdir(folder_path)
        else:
            raise InvalidPathError(f"Path {requested_full_path} is not safe.")

    def create_model_card(self, grid_search_id: str, experiment_id: str) -> Dict:
        """
        Fetch Model card info if available or else create & store model card info in event storage.
        :params:
                grid_search_id (str): Grid Search ID
                experiment_id (str): Experiment ID

        :returns: model_card (Dict): Model card infomration for the experiment.
        """
        try:
            requested_full_path = os.path.realpath(
                os.path.join(self.top_level_logging_path, str(grid_search_id), str(experiment_id), f"model_card.json")
            )
            if FileDataAccess.is_safe_path(base_dir=self.top_level_logging_path, requested_path=requested_full_path):
                if not os.path.isfile(requested_full_path):
                    checkpoint_list = self.get_checkpoint_list(grid_search_id=grid_search_id, experiment_id=experiment_id)
                    epoch = checkpoint_list[0]["epoch"]
                    for checkpoint in checkpoint_list:
                        if checkpoint["epoch"] > epoch:
                            epoch = checkpoint["epoch"]

                    model_state_buffer = self.get_checkpoint_resource(
                        grid_search_id=grid_search_id,
                        experiment_id=experiment_id,
                        epoch=epoch,
                        checkpoint_resource=CheckpointResource.model,
                    )

                    model_state = torch.load(model_state_buffer)
                    model = NNModel()
                    model.load_state_dict(model_state, strict=False)

                    exp_config = self.load_config(
                        grid_search_id=grid_search_id, config_name="experiment_config", file_type="json", experiment_id=experiment_id
                    )
                    gs_config = self.load_config(grid_search_id=grid_search_id, config_name="grid_search_config", file_type="yml")

                    model_card = ModelCardFactory.create_model_card(
                        grid_search_id=grid_search_id, exp_config=exp_config, gs_config=gs_config, model=model
                    )
                    payload_dict = RawTextFile(file_format=FileFormat.JSON, content=json.dumps(model_card))
                    self.add_config_to_experiment(
                        grid_search_id=grid_search_id, experiment_id=experiment_id, config_name="model_card.json", config=payload_dict
                    )
                    return model_card
                else:
                    return json.loads(Path(requested_full_path).read_text())
            else:
                raise InvalidPathError(f"File path {requested_full_path} is not safe.")
        except ModelCardFetchError as e:
            raise ModelCardFetchError(f"Unable to create/save Model Card") from e
