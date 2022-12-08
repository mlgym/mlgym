from multiprocessing import Queue, Process
from ml_board.backend.messaging.events import Event
from abc import ABC
from typing import List, Dict
from ml_board.backend.messaging.event_storage import EventStorageIF


class PublishingIF(ABC):

    def publish_event(self, event: Event):
        raise NotImplementedError


class BrokerIF(ABC):
    def listen_for_events(self, event_queue: Queue):
        raise NotImplementedError


class SubscriberIF:

    def update_event(self, event: Event):
        raise NotImplementedError


class Broker(Process, BrokerIF):

    def __init__(self, event_storage: EventStorageIF, event_queue: Queue):
        super().__init__(target=self.work, args=(event_queue, ))

        self._event_storage: EventStorageIF = event_storage
        self._event_queue = event_queue
        # maps subscriber to the last event id
        self._subscribers: Dict[SubscriberIF, int] = {}

    def listen_for_events(self, event_queue: Queue):
        while True:
            event = event_queue.get()
            self._publish_event(event)

    def _update_subscribers(self):
        for subscriber, last_event_id in self._subscribers.items():
            while self._event_storage.has_next(last_event_id):
                last_event_id, event = self._event_storage.get_next(last_event_id)
                subscriber.update_event(event)
                self._subscribers[subscriber] = last_event_id

    def _publish_event(self, event: Event):
        self._message_queue.put(event)
        self._update_subscribers()

    def add_subscriber(self, subscriber: SubscriberIF):
        self._subscribers[subscriber] = 0


class Publisher(PublishingIF):
    def __init__(self, event_queue: Queue):
        self._event_queue = event_queue

    def publish_event(self, event: Event):
        self._event_queue.put(event)
