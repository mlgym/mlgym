from genericpath import isdir
from ml_gym.backend.messaging.events import Event
from abc import ABC
from typing import List, Tuple, Dict, Generator
from ml_gym.error_handling.exception import EventStorageInvalidIndexingError
from collections import defaultdict
import os
import json


class EventStorageIF(ABC):

    def add_event(self, event_storage_id: str, event: Event) -> int:
        raise NotImplementedError

    def get_event(self, event_storage_id: str,  event_id: int) -> Event:
        raise NotImplementedError

    def iter_generator(self, event_storage_id: str = None):  # -> Generator[Tuple[str, Event]]:
        raise NotImplementedError

    def length(self, event_storage_id: str = None) -> int:
        raise NotImplementedError

    @property
    def event_storage_ids(self) -> List[str]:
        raise NotImplementedError


class ListEventStorage(EventStorageIF):
    def __init__(self):
        self._storage: Dict[str, List[Event]] = defaultdict(list)

    def add_event(self, event_storage_id: str, event: Event) -> int:
        # TODO make this thing thread / multiprocessing safe
        # if we use the async_mode eventlet, locking is not necessary
        # see: https://stackoverflow.com/questions/2851499/eventlet-and-locking
        event_id = len(self._storage[event_storage_id])
        self._storage[event_storage_id].append(event)
        return event_id

    # def get_event(self, event_storage_id: str, event_id: int) -> Event:
    #     if len(self._storage[event_storage_id])-1 < event_id:
    #         raise EventStorageInvalidIndexingError(f"Could not access event at index {event_id}.")
    #     return self._storage[event_storage_id][event_id]

    def iter_generator(self, event_storage_id: str = None):  # -> Generator[Tuple[str, Event]]:
        if event_storage_id is None:
            event_storage_ids = list(self._storage.keys())
            if event_storage_ids:
                event_storage_id = list(self._storage.keys())[-1]
                current = 0
                while current < len(self._storage[event_storage_id]):
                    yield current, self._storage[event_storage_id][current]
                    current += 1
            else:
                return iter(())

    def length(self, event_storage_id: str = None) -> int:
        if event_storage_id not in self._storage:
            return 0
        return len(self._storage[event_storage_id])

    @property
    def event_storage_ids(self) -> List[str]:
        return list(self._storage.keys())


class DiscEventStorage(EventStorageIF):
    def __init__(self, logging_path: str):
        self._logging_path = logging_path
        os.makedirs(self._logging_path, exist_ok=True)
        self._event_storage_ids = [element for element in os.listdir(self._logging_path) if os.path.isdir(os.path.join(self._logging_path, element))]

    def add_event(self, event_storage_id: str, event: Event) -> int:
        if event_storage_id not in self._event_storage_ids:
            self._add_event_storage(self._logging_path, event_storage_id)

        event_id = self.length(event_storage_id)

        full_path = os.path.join(self._logging_path, event_storage_id, "event_storage.log")
        with open(full_path, "a") as fd:
            json_event = json.dumps(event)
            fd.write(f"{json_event}\n")

        return event_id

    def iter_generator(self, event_storage_id: str = None):  # -> Generator[Tuple[str, Event]]:
        full_path = os.path.join(self._logging_path, event_storage_id, "event_storage.log")
        event_id = 0
        with open(full_path, "r") as fd:
            for line in fd:
                event = json.loads(line)
                yield event_id, event
                event_id += 1

    def length(self, event_storage_id: str = None) -> int:
        full_path = os.path.join(self._logging_path, event_storage_id, "event_storage.log")
        if not os.path.exists(full_path):
            return 0
        else:
            with open(full_path, "r") as fd:
                return len(fd.readlines())  # TODO this is very ineffecient! We should cache this information.

    def _add_event_storage(self, logging_path: str, event_storage_id: str):
        full_path = os.path.join(logging_path, event_storage_id)
        os.mkdir(full_path)
        self._event_storage_ids.append(event_storage_id)
        return full_path

    @property
    def event_storage_ids(self) -> List[str]:
        return self._event_storage_ids


class EventStorageFactory:
    @staticmethod
    def get_list_event_storage() -> EventStorageIF:
        return ListEventStorage()

    @staticmethod
    def get_disc_event_storage(logging_path: str) -> EventStorageIF:
        return DiscEventStorage(logging_path)
