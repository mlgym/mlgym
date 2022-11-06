from ml_board.backend.messaging.events import Event
from abc import ABC
from typing import List
import os
import json
from pathlib import Path


class EventStorageIF(ABC):

    def add_event(self, event: Event) -> int:
        raise NotImplementedError

    def get_event(self, event_id: int) -> Event:
        raise NotImplementedError

    def iter_generator(self):  # -> Generator[Tuple[str, Event]]:
        raise NotImplementedError

    def length(self) -> int:
        raise NotImplementedError


class ListEventStorage(EventStorageIF):
    def __init__(self):
        self._storage: List[Event] = list()

    def add_event(self, event: Event) -> int:
        # TODO make this thing thread / multiprocessing safe
        # if we use the async_mode eventlet, locking is not necessary
        # see: https://stackoverflow.com/questions/2851499/eventlet-and-locking
        event_id = len(self._storage)
        self._storage.append(event)
        return event_id

    # def get_event(self, event_storage_id: str, event_id: int) -> Event:
    #     if len(self._storage[event_storage_id])-1 < event_id:
    #         raise EventStorageInvalidIndexingError(f"Could not access event at index {event_id}.")
    #     return self._storage[event_storage_id][event_id]

    def iter_generator(self):  # -> Generator[Tuple[str, Event]]:
        current = 0
        while current < len(self._storage):
            yield current, self._storage[current]
            current += 1

    def length(self) -> int:
        return len(self._storage)


class DiscEventStorage(EventStorageIF):
    def __init__(self, parent_dir: str, event_storage_id: str):
        self._event_storage_id = event_storage_id
        # create even_storage log if it does not exist yet
        self.log_dir_path = os.path.join(parent_dir, event_storage_id)
        self.log_path = os.path.join(parent_dir, event_storage_id, "event_storage.log")
        Path(self.log_dir_path).mkdir(parents=True, exist_ok=True)
        Path(self.log_path).touch(exist_ok=True)

    def add_event(self, event: Event) -> int:
        event_id = self.length()  # need to check for possible race condition

        with open(self.log_path, "a") as fd:
            json_event = json.dumps(event)
            fd.write(f"{json_event}\n")

        return event_id

    def iter_generator(self):  # -> Generator[Tuple[str, Event]]:
        event_id = 0
        with open(self.log_path, "r") as fd:
            for line in fd:
                event = json.loads(line)
                yield event_id, event
                event_id += 1

    def length(self) -> int:
        with open(self.log_path, "r") as fd:
            # TODO make this thing thread / multiprocessing safe
            # if we use the async_mode eventlet, locking is not necessary
            # see: https://stackoverflow.com/questions/2851499/eventlet-and-locking
            return len(fd.readlines())  # TODO this is very ineffecient! We should cache this information.

    @property
    def event_storage_ids(self) -> List[str]:
        return self._event_storage_ids


class EventStorageFactory:
    @staticmethod
    def get_list_event_storage() -> EventStorageIF:
        return ListEventStorage()

    @staticmethod
    def get_disc_event_storage(parent_dir: str, event_storage_id: str) -> EventStorageIF:
        return DiscEventStorage(parent_dir, event_storage_id)
