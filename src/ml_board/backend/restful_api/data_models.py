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


# TODO Check if Enum is still needed
class CheckpointResource(str, Enum):
    model = "model.pickle"
    optimizer = "optimizer.pickle"
    lr_scheduler = "lr_scheduler.pickle"
    stateful_components = "stateful_components.pickle"
    accelerate = "accelerate_zip.pickle"
