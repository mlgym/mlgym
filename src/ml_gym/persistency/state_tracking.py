from abc import abstractmethod
from typing import Dict, BinaryIO
from dashify.logging.dashify_logging import ExperimentInfo
from ml_gym.persistency.io import DashifyWriter


class StateTrackableIF:

    @abstractmethod
    def get_state_representation(self) -> BinaryIO:
        raise NotImplementedError

    @abstractmethod
    def load_state_representation(self, representation: BinaryIO):
        raise NotImplementedError


class StateTrackerIF:

    @abstractmethod
    def register_trackable(self, trackable: StateTrackableIF):
        raise NotImplementedError

    @abstractmethod
    def save_state(self, measurement_id: int = 0):
        raise NotImplementedError


class StateTracker(StateTrackerIF):

    def __init__(self):
        super().__init__()
        self.trackables: Dict[str, StateTrackableIF] = {}

    def register_trackable(self, key: str, trackable: StateTrackableIF):
        self.trackables[key] = trackable


class DiscStateTracker(StateTracker):

    def __init__(self, experiment_info: ExperimentInfo):
        super().__init__()
        self.experiment_info = experiment_info
        self.trackables: Dict[str, StateTrackableIF] = {}

    def save_state(self, measurement_id: int = 0):
        states = {key: trackable.get_state_representation() for key,  trackable in self.trackables.items()}
        for key, state in states.items():
            DashifyWriter.save_binary_state(key=key,
                                            state=state,
                                            experiment_info=self.experiment_info,
                                            measurement_id=measurement_id)
