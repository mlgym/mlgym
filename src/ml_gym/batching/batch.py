import torch
from abc import abstractmethod, ABC
from typing import Dict, List, Any, Callable
from ml_gym.error_handling.exception import BatchStateError
import copy


class TorchDeviceMixin(ABC):

    @staticmethod
    def _dict_tensor_to_device(d: Dict[str, Any], device: torch.device) -> Dict[str, Any]:
        return {k: TorchDeviceMixin._dict_tensor_to_device(v, device) if not isinstance(v, torch.Tensor) else v.to(device) for k, v in d.items()}

    @staticmethod
    def _detach_dict_tensor(d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: TorchDeviceMixin._detach_dict_tensor(v) if not isinstance(v, torch.Tensor) else v.detach() for k, v in d.items()}

    @abstractmethod
    def get_device(self) -> torch.device:
        raise NotImplementedError

    @abstractmethod
    def to_device(self, device: torch.device):
        raise NotImplementedError

    @abstractmethod
    def detach(self):
        raise NotImplementedError

    @abstractmethod
    def to_cpu(self):
        raise NotImplementedError


class Batch(ABC):
    """Abstract class that defines the necessary methods any `Batch` implementation needs to implement.
    """

    @staticmethod
    def combine(batches: List['Batch']):
        batch_combined = batches[0].__class__.combine_impl(batches)
        return batch_combined

    @staticmethod
    def _copy_tensor_dict(d: Dict[Any, torch.Tensor]):
        return {k: v.clone() for k, v in d.items()}

    @staticmethod
    def _combine_tensor_dicts(tensor_dicts: List[Dict[Any, torch.Tensor]]) -> Dict[Any, torch.Tensor]:
        combined_tensor_dict = {}
        for key in tensor_dicts[0].keys():
            if isinstance(tensor_dicts[0][key], dict):
                sub_tensor_dicts = [d[key] for d in tensor_dicts]
                combined_tensor_dict[key] = Batch._combine_tensor_dicts(sub_tensor_dicts)
            else:
                combined_tensor_dict[key] = torch.cat([d[key] for d in tensor_dicts])
        return combined_tensor_dict

    @staticmethod
    @abstractmethod
    def combine_pair(b_1: 'Batch', b_2: 'Batch') -> 'Batch':
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def combine_impl(batches: List['Batch']) -> 'Batch':
        raise NotImplementedError


class DatasetBatch(Batch, TorchDeviceMixin):
    """A batch of samples and its targets and tags. Used to batch train a model."""

    def __init__(self, samples: torch.Tensor, targets: Dict[str, torch.Tensor], tags: torch.Tensor = None):
        self._samples = samples
        self._targets = targets
        self._tags = tags if tags is not None else torch.Tensor()

    @property
    def samples(self) -> torch.Tensor:
        return self._samples

    @property
    def targets(self) -> Dict[str, torch.Tensor]:
        return self._targets

    @property
    def tags(self) -> torch.Tensor:
        return self._tags

    def detach(self):
        self._targets = {k: v.detach() for k, v in self._targets.items()}
        self._tags = self._tags.detach()
        self._samples = self._samples.detach()

    def to_device(self, device: torch.device):
        self._samples = self._samples.to(device)
        self._targets = {k: v.to(device) for k, v in self._targets.items()}
        self._tags = self._tags.to(device)

    def to_cpu(self):
        self.to_device(device=torch.device("cpu"))

    def get_device(self) -> torch.device:
        return self._samples.device

    @staticmethod
    def combine_impl(batches: List['DatasetBatch']) -> 'DatasetBatch':
        tags = torch.cat([batch.tags for batch in batches])
        samples = torch.cat([batch.samples for batch in batches])
        targets = Batch._combine_tensor_dicts([batch.targets for batch in batches])
        return DatasetBatch(targets=targets, samples=samples, tags=tags)

    def __len__(self) -> int:
        return len(self._samples)

    def __deepcopy__(self, memo) -> 'DatasetBatch':
        samples_ = self.samples.clone()
        targets_ = self._copy_tensor_dict(self.targets)
        tags_ = self.tags.clone()
        return DatasetBatch(samples=samples_, targets=targets_, tags=tags_)

    @staticmethod
    def combine_pair(b_1: 'DatasetBatch', b_2: 'DatasetBatch') -> 'DatasetBatch':
        b_1 = copy.deepcopy(b_1)
        b_2 = copy.deepcopy(b_2)
        tags = torch.cat([b_1.tags, b_2.tags])
        samples = torch.cat([b_1.samples, b_2.samples])
        targets = Batch._combine_tensor_dicts([b_1.targets, b_2.targets])
        return DatasetBatch(targets=targets, samples=samples, tags=tags)


class InferenceResultBatch(Batch, TorchDeviceMixin):
    """ Stores targets and predictions of an entire batch.
    """

    def __init__(self, targets: Dict[str, torch.Tensor] = None, predictions: Dict[str, torch.Tensor] = None, tags: torch.Tensor = None):
        self._targets = targets if targets is not None else {}
        self._tags = tags
        self._predictions = predictions if predictions is not None else {}

    def to_cpu(self):
        self.to_device(device=torch.device("cpu"))

    def get_device(self) -> torch.device:
        return self._tags.device

    def to_device(self, device: torch.device):
        if isinstance(self._predictions, torch.Tensor):
            self._predictions = self._predictions.to(device)
        else:
            self._predictions = TorchDeviceMixin._dict_tensor_to_device(self._predictions, device)
        self._targets = {k: v.to(device) for k, v in self._targets.items()}
        self._tags = self._tags.to(device)

    def detach(self):
        self._targets = {k: v.detach() for k, v in self._targets.items()}
        self._tags = self._tags.detach()
        if isinstance(self._predictions, torch.Tensor):
            self._predictions = self._predictions.detach()
        else:
            self._predictions = TorchDeviceMixin._detach_dict_tensor(self._predictions)

    @property
    def predictions(self) -> Dict[str, torch.Tensor]:
        return self._predictions

    def add_predictions(self, key: str, predictions: torch.Tensor):
        self._predictions[key] = predictions

    def get_predictions(self, key: str) -> torch.Tensor:
        if key not in self._predictions:
            raise BatchStateError(f"Key {key} not present in predictions!")
        return self._predictions[key]

    def drop_predictions(self, keys: List[str]):
        for key in keys:
            del self._predictions[key]

    def drop_targets(self, keys: List[str]):
        for key in keys:
            del self._targets[key]

    def get_targets(self, key: str) -> torch.Tensor:
        if key not in self._targets:
            raise BatchStateError(f"Key {key} not present in targets!")
        return self._targets[key]

    def add_targets(self, key: str, targets: torch.Tensor):
        self._targets[key] = targets

    @property
    def targets(self) -> Dict[str, torch.Tensor]:
        return self._targets

    @property
    def tags(self) -> torch.Tensor:
        return self._tags

    def __len__(self) -> int:
        return len(self._tags)

    def __deepcopy__(self, memo) -> 'InferenceResultBatch':
        predictions_ = self._copy_tensor_dict(self.predictions)
        targets_ = self._copy_tensor_dict(self.targets)
        tags_ = self.tags.clone()
        return InferenceResultBatch(predictions=predictions_, targets=targets_, tags=tags_)

    def split_results(self, target_keys: List[str], predictions_keys: List[str], device: torch.device):
        targets = {key: self._targets[key].to(device) for key in target_keys}
        predictions = {key: self._predictions[key].to(device) for key in predictions_keys}
        tags = self.tags.to(device)
        return InferenceResultBatch(targets=targets, predictions=predictions, tags=tags)

    @staticmethod
    def combine_pair(b_1: 'InferenceResultBatch', b_2: 'InferenceResultBatch') -> 'InferenceResultBatch':
        # tags = torch.cat([b_1.tags, b_2.tags])
        tags = b_1.tags + b_2.tags
        predictions = Batch._combine_tensor_dicts([b_1.predictions, b_2.predictions])
        targets = Batch._combine_tensor_dicts([b_1.targets, b_2.targets])
        return InferenceResultBatch(targets=targets, predictions=predictions, tags=tags)

    @staticmethod
    def combine_impl(batches: List['InferenceResultBatch']) -> 'InferenceResultBatch':
        tags = [tag for batch in batches for tag in batch.tags]
        predictions = Batch._combine_tensor_dicts([batch.predictions for batch in batches])
        targets = Batch._combine_tensor_dicts([batch.targets for batch in batches])
        return InferenceResultBatch(targets=targets, predictions=predictions, tags=tags)


class EvaluationBatchResult(Batch):
    """Data class for storing the results of a single or multiple batches. Also entire epoch results are stored in here.
    """

    def __init__(self, losses: Dict[str, List[float]], metrics: Dict[str, List[float]], dataset_name: str,
                 split_name: str):
        self._losses = losses
        self._metrics = metrics
        self._dataset_name = dataset_name
        self._split_name = split_name

    @property
    def losses(self) -> Dict[str, List[float]]:
        return self._losses

    @property
    def metrics(self) -> Dict[str, List[float]]:
        return self._metrics

    @property
    def dataset_name(self) -> str:
        return self._dataset_name

    @property
    def split_name(self) -> str:
        return self._split_name

    def aggregate(self, fun: Callable[[List], List] = None):
        if fun is None:
            def fun(e): return [sum(e)]
        self._losses = {k: fun(v) for k, v in self._losses.items()}
        self._metrics = {k: fun(v) for k, v in self._metrics.items()}

    @staticmethod
    def combine_pair(b_1: 'EvaluationBatchResult', b_2: 'EvaluationBatchResult') -> 'EvaluationBatchResult':
        raise NotImplementedError

    @staticmethod
    def combine_impl(batches: List['EvaluationBatchResult']) -> 'EvaluationBatchResult':
        raise NotImplementedError

    def __str__(self) -> str:
        eval_str = f"Evaluation result on {self._dataset_name} ({self._dataset_split}):"
        eval_str += "\n\nlosses: " + "\n\t".join([f"{k}: {v}" for k, v in self._losses.items()])
        eval_str += "\n\nmetrics: " + "\n\t".join([f"{k}: {v}" for k, v in self._metrics.items()])
        eval_str += "\n==============================================="
        return eval_str

    def to_dict(self) -> Dict[str, Any]:
        results = {str(k): v for k, v in self.metrics.items()}
        for k, v in self.losses.items():
            k = str(k)
            if str(k) in results:
                raise BatchStateError("Metrics keys and losses keys must be distinct")
            else:
                results[k] = v
        return results
