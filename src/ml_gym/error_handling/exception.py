class DatasetNotFoundError(Exception):
    """Exception raised when a dataset could not be found."""
    pass


class DatasetOutOfBoundsError(Exception):
    """Exception raised when an index >= len(Dataset) is used."""
    pass


class ModelNotTrainedError(Exception):
    """Exception raised when model state is requested that is training dependent"""
    pass


class ModelAlreadyFullyTrainedError(Exception):
    """Exception raised when model is fully trained but training for another epoch was initiated."""
    pass


class TrainingStateCorruptError(Exception):
    """Raised e.g., when the number of checkpointed models does not match the number of evaluations in the metrics.json"""


class DatasetFileCorruptError(Exception):
    """Thrown when integrity checks indicate that a given file is corrupt."""
    pass


class LossFunctionInitError(Exception):
    """Exception raised when a loss function cannot be initiliazed"""
    pass


class BatchStateError(Exception):
    """Exception raised when a Batch object does not contain the requested data"""
    pass


class ExperimentInfoMissing(Exception):
    """Exception raised when experiment info object is missing"""
    pass


class ComponentConstructionError(Exception):
    """Exception raised when an error occurred during component construction"""
    pass


class DependentComponentNotFoundError(Exception):
    """Exception raised when a component required by a parent component could not be found"""
    pass


class SingletonAlreadyInstantiatedError(Exception):
    """Exception raised when trying to get another instance from a singleton class"""
    pass


class InjectMappingNotFoundError(Exception):
    """Exception raised when Injector cannot inject given placehold when it was not defined in the mapping."""
    pass


class ValidationModeNotValidError(Exception):
    """Exception when an invalid validation mode was selected."""
    pass


class InvalidTensorFormatError(Exception):
    """Raised when a torch tensor has the wrong format for subsequent computation"""


class OptimizerNotInitializedError(Exception):
    """Raised when we want to run an operation on an optimizer, which was not instantiated, yet."""
    pass
