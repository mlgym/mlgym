from enum import Enum
from fastapi import FastAPI
import os
import glob
from fastapi import status, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
# from ml_gym.util.util import YAMLConfigLoader
from pydantic import BaseModel
import re
from typing import Dict
import json


class FileFormat(str, Enum):
    YAML = "YAML"
    JSON = "JSON"


# [{"experiment_id": experiment_id,
#                      "last_checkpoint_id": last_checkpoint_id,
#                      "experiment_config": load_experiment_config(top_level_logging_path, grid_search_id, experiment_id)}

class ExperimentStatus(BaseModel):
    experiment_id: int
    last_checkpoint_id: int
    experiment_config: Dict


class RawTextFile(BaseModel):
    file_format: FileFormat
    content: str


app = FastAPI(port=8080)


class CheckpointResource(str, Enum):
    model = "model"
    optimizer = "optimizer"
    stateful_components = "stateful_components"


def is_safe_path(base_dir, requested_path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(requested_path)
    else:
        matchpath = os.path.abspath(requested_path)
    return base_dir == os.path.commonpath((base_dir, matchpath))


def get_checkpoint_files(path: str, base_path: str):
    full_paths = glob.glob(os.path.join(path, "**", "*.bin"), recursive=True)
    return [os.path.relpath(full_path, base_path) for full_path in full_paths]


def iterfile(file_path: str):
    with open(file_path, mode="rb") as file_like:
        yield from file_like


@app.get('/grid_searches/{grid_search_id}/experiments')
def get_experiment_statuses(grid_search_id: str):
    def get_last_checkpoint_ids(top_level_logging_path: str, grid_search_id: str) -> Dict:
        paths = glob.glob(os.path.join(top_level_logging_path, grid_search_id, '**/*'), recursive=True)
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

    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, grid_search_id))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        epxeriment_id_to_last_checkpoint_id = get_last_checkpoint_ids(top_level_logging_path, grid_search_id)
        response = [ExperimentStatus(**{"experiment_id": experiment_id,
                                        "last_checkpoint_id": last_checkpoint_id,
                                        "experiment_config": load_experiment_config(top_level_logging_path, grid_search_id, experiment_id)})
                    for experiment_id, last_checkpoint_id in epxeriment_id_to_last_checkpoint_id.items()]
        return response

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


# @app.get('/grid_searches/{grid_search_id}/gs_config')
# def get_grid_search_config(grid_search_id: str):
#     requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), "gs_config.yml"))

#     if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
#         return YAMLConfigLoader.load(requested_full_path)

#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f'Provided unsafe filepath {requested_full_path}')


@app.put('/grid_searches/{grid_search_id}/{config_name}')
def add_raw_config_to_grid_search(grid_search_id: str, config_name: str, config_file: RawTextFile):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), config_name))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        os.makedirs(os.path.dirname(requested_full_path), exist_ok=True)
        with open(requested_full_path, "w") as fp:
            fp.writelines(config_file.content)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


@app.put('/grid_searches/{grid_search_id}/{experiment_id}/{config_name}')
def add_config_to_experiment(grid_search_id: str, experiment_id: str, config_name: str, config: RawTextFile):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), str(experiment_id), config_name))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        os.makedirs(os.path.dirname(requested_full_path), exist_ok=True)
        with open(requested_full_path, "w") as fp:
            fp.writelines(config.content)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


@app.get('/checkpoints/{grid_search_id}/{experiment_id}/{epoch}/{checkpoint_resource}')
def get_checkpoint_resource(grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), str(experiment_id),
                                                        str(epoch), f"{checkpoint_resource}.bin"))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        if not os.path.isfile(requested_full_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Resource {requested_full_path} does not exist')
        return StreamingResponse(iterfile(requested_full_path), media_type="application/octet-stream")

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


@app.get('/checkpoints/{grid_search_id}/{experiment_id}/{epoch}')
def get_checkpoint_list_epoch(grid_search_id: str, experiment_id: str, epoch: str):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), str(experiment_id), str(epoch)))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        files = get_checkpoint_files(requested_full_path, base_path=top_level_logging_path)
        return {os.path.basename(file).split(".")[0]: file for file in files}

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


if __name__ == "__main__":
    top_level_logging_path = os.path.abspath("/home/mluebberin/repositories/github/private_workspace/mlgym/src/ml_board/backend/websocket_api/event_storage/logs")

    port = 5001
    uvicorn.run(app, host="0.0.0.0", port=port)
