from ml_gym.backend.messaging.events import Event
from abc import ABC
from typing import List, Tuple
from ml_gym.error_handling.exception import EventStorageInvalidIndexingError
from regex import R


class EventStorageIF(ABC):

    def add_event(self, event: Event):
        raise NotImplementedError

    def get_event(self, event_id: int) -> Event:
        raise NotImplementedError

    def __iter__(self) -> Tuple[str, Event]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class ListEventStorage(EventStorageIF):
    def __init__(self):
        self._storage: List[Event] = []

    def __len__(self) -> int:
        return len(self._storage)

    def add_event(self, event: Event):
        # TODO make this thing thread / multiprocessing safe
        event_id = len(self._storage)
        self._storage.append(event)
        return event_id

    def get_event(self, event_id: int) -> Event:
        if len(self._storage)-1 < event_id:
            raise EventStorageInvalidIndexingError(f"Could not access event at index {event_id}.")
        return self._storage[event_id]

    def __iter__(self) -> Tuple[str, Event]:
        current = 0
        stop = len(self._storage)
        while current < stop:
            yield current, self._storage[current]
            current += 1


class EventStorageFactory:
    @staticmethod
    def get_list_event_storage() -> ListEventStorage:
        return ListEventStorage()
