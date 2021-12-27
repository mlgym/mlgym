from ml_gym.backend.messaging.events import Event
from abc import ABC
from typing import List, Tuple
from ml_gym.error_handling.exception import EventStorageInvalidIndexingError


class EventStorageIF(ABC):

    def add_event(self, event: Event):
        raise NotImplementedError

    def get_event(self, event_id: int) -> Event:
        raise NotImplementedError

    def get_last_event_key(self) -> int:
        raise NotImplementedError

    def has_next(self, event_id: int) -> bool:
        raise NotImplementedError

    def get_next(self, last_event_id: int) -> Tuple[int, Event]:
        raise NotImplementedError


class ListEventStorage(EventStorageIF):

    def __init__(self):
        self._storage: List[Event] = []

    def add_event(self, event: Event):
        self._storage.append(event)

    def get_event(self, event_id: int) -> Event:
        if len(self._storage)-1 < event_id:
            raise EventStorageInvalidIndexingError(f"Could not access event at index {event_id}.")
        return self._storage[event_id]

    def has_next(self, event_id: int) -> bool:
        return event_id + 1 < len(self._storage)

    def get_next(self, last_event_id: int) -> Tuple[int, Event]:
        return last_event_id+1, self.get_event(last_event_id+1)
