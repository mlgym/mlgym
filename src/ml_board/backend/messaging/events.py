from dataclasses import dataclass
from typing import Dict


@dataclass
class Event:
    creation_timestamp: int
    message: Dict
    origin: str
