
class EventStorageInvalidIndexingError(Exception):
    """Raised when an event is tried to indexed within the event storage but the index is not present."""