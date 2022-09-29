from enum import Enum
from fastapi import FastAPI
import os
import glob
from fastapi import status, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
from ml_gym.util.util import YAMLConfigLoader
from pydantic import BaseModel


class FileFormat(str, Enum):
    YAML = "YAML"
    JSON = "JSON"


class RawTextFile(BaseModel):
    file_format: FileFormat
    content: str


app = FastAPI(port=8080)


class CheckpointResource(str, Enum):
    model = "model"
    optimizer = "optimizer"
    stateful_component = "stateful_component"


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


@app.get('/grid_searches/{grid_search_id}/gs_config')
def get_grid_search_config(grid_search_id: str):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), "gs_config.yml"))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
        return YAMLConfigLoader.load(requested_full_path)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Provided unsafe filepath {requested_full_path}')


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
def get_checkpoint(grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource):
    requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), str(experiment_id),
                                                        str(epoch), f"{checkpoint_resource}.bin"))

    if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
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
