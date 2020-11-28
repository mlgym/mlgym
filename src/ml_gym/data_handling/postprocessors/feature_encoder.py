from abc import ABC, abstractmethod
import numpy as np
from typing import Dict
from sklearn.preprocessing import StandardScaler


class Encoder(ABC):
    @abstractmethod
    def fit(self):
        raise NotImplementedError

    @abstractmethod
    def transform(self):
        raise NotImplementedError

    @abstractmethod
    def get_output_size(self) -> int:
        raise NotImplementedError


class CategoricalEncoder(Encoder):
    def __init__(self):
        super().__init__()
        self.all_values: set = None
        self.value_to_ix: Dict[str, int] = None
        self.ix_to_value: Dict[int, str] = None

    def fit(self, values: np.ndarray):
        self.all_values = np.unique(values.flatten())
        self.value_to_ix = {str(value): ix for ix, value in enumerate(self.all_values)}
        self.ix_to_value = {ix: str(value) for ix, value in enumerate(self.all_values)}

    def transform(self, values: np.ndarray) -> np.ndarray:
        def to_one_hot(value):
            encoded = np.zeros(len(self.all_values))
            encoded[self.value_to_ix[str(value)]] = 1
            return encoded

        if self.all_values is None:
            raise Exception("Please call fit() before transform()")

        transformed = np.array([to_one_hot(value) for value in values.flatten()])
        return transformed

    def get_output_size(self) -> int:
        return len(self.all_values)


class ContinuousEncoder(Encoder):
    def __init__(self):
        super().__init__()
        self.sklearn_encoder = None

    def fit(self, values: np.ndarray):
        self.sklearn_encoder = StandardScaler()
        self.sklearn_encoder.fit(np.expand_dims(values, axis=1))

    def transform(self, values: np.ndarray) -> np.ndarray:
        if self.sklearn_encoder is None:
            raise Exception("Please call fit() before transform()")
        return self.sklearn_encoder.transform(np.expand_dims(values, axis=1))

    def get_output_size(self) -> int:
        return 1
