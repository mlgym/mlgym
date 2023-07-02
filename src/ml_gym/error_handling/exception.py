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


class EvaluationError(Exception):
    """Exception raised when somthing goes wrong within the evaluation."""
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


class ClassRegistryKeyNotFoundError(Exception):
    """Exception raised when requested key is not present in the class registry"""
    pass


class ClassRegistryItemInstantiationError(Exception):
    """Raised when an item in the class registry could not be built"""
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


class LRSchedulerNotInitializedError(Exception):
    """Raised when we want to run an operation on a lr scheduler, which was not instantiated, yet."""
    pass


class MetricCalculationError(Exception):
    """Raised when there was an error during metric calculation"""
    pass


class LossCalculationError(Exception):
    """Raised when there was an error during loss calculation"""
    pass


class SamplerNotFoundError(Exception):
    """Raised when the sampler implemenation for a given datsetloader was not found."""
    pass


class NetworkError(Exception):
    """Raised when there is a network or connetion error."""
    pass


class DataIntegrityError(Exception):
    """Raised when the data is not in the expected format."""
    pass


class InvalidPathError(Exception):
    """Raised when the path to a file or directory is invalid/corrupt."""
    pass


class CheckpointEntityError(Exception):
    """Raised when there is an error within the checkpoint entity."""
    pass


class EarlyStoppingCriterionFulfilledError(Exception):
    """Raised when the early stopping criterion in the gym job was fulfilled."""
    pass


class GymError(Exception):
    """Raised when an error occurs within the gym or during gym instantiation."""
    pass

class SystemInfoFetchError(Exception):
    """Raised when an error occurs during fetching system information."""
    pass

class ModelCardCreationError(Exception):
    """Raised when an error occurs during creation of model card."""
    pass

class ModelDetailsCreationError(Exception):
    """Raised when an error occurs during creation of ModelDetails object in model card."""
    pass

class DatasetDetailsCreationError(Exception):
    """Raised when an error occurs during creation of DatasetDetails object in model card."""
    pass

class TrainingDetailsCreationError(Exception):
    """Raised when an error occurs during creation of TrainingDetails object in model card."""
    pass

class EvalDetailsCreationError(Exception):
    """Raised when an error occurs during creation of EvalDetails object in model card."""
    pass

class PipelineDetailsCreationError(Exception):
    """Raised when an error occurs during creation of PipelineDetails object in model card."""
    pass
