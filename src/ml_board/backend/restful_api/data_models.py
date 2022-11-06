from pydantic import BaseModel
from enum import Enum
from typing import Dict


class FileFormat(str, Enum):
    YAML = "YAML"
    JSON = "JSON"


class RawTextFile(BaseModel):
    file_format: FileFormat
    content: str


class ExperimentStatus(BaseModel):
    experiment_id: int
    last_checkpoint_id: int
    experiment_config: Dict


class CheckpointResource(str, Enum):
    model = "model"
    optimizer = "optimizer"
    stateful_components = "stateful_components"
