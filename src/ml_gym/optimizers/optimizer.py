from torch.optim.optimizer import Optimizer
from functools import partial
from typing import Dict, Any, Type
from copy import deepcopy
from ml_gym.error_handling.exception import OptimizerNotInitializedError


class OptimizerAdapter(object):

    def __init__(self, optimizer_class: Type[Optimizer], optimizer_params: Dict = None):
        self._optimizer_class = optimizer_class
        self._optimizer_params = optimizer_params if optimizer_params is not None else {}

        self._optimizer: Optimizer = None
        self._state_dict = None

    def register_model_params(self, model_params: Dict, restore_state: bool=True):
        if not restore_state:
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params)
            return

        # since we instantiate a new optimizer when we register a model, we have to save and restore the optimizer state
        if self._optimizer is not None:
            state_dict = self.state_dict()
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params)
            self.load_state_dict(state_dict)
        else:
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params)
            if self._state_dict is not None:
                self._optimizer.load_state_dict(self._state_dict)
                self._state_dict = None

    def __getstate__(self):
        if self._optimizer is not None:
            return self._optimizer.__getstate__()
        else:
            return {}

    def __setstate__(self, state):
        if not hasattr(self, '_optimizer'):
            self._optimizer = None
        if self._optimizer is not None:
            self._optimizer.__setstate__(state)

    def __repr__(self):
        return self._optimizer.__repr__()

    def _hook_for_profile(self):
        self._optimizer._hook_for_profile()

    def state_dict(self) -> Dict[str, Any]:
        if self._optimizer is not None:
            return self._optimizer.state_dict()
        elif self._state_dict is not None:
            return self._state_dict
        else:
            raise OptimizerNotInitializedError("Cannot access state_dict, because internal optimizer was not instantiated.")


    def load_state_dict(self, state_dict: Dict):
        if self._optimizer is not None:
            self._optimizer.load_state_dict(state_dict)
        else:  # here we store the state_dict until we instantiate the optimizer
            self._state_dict = state_dict

    def zero_grad(self, set_to_none: bool = False):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.zero_grad(set_to_none)

    def step(self, closure=None):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.step(closure)

    def add_param_group(self, param_group):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.add_param_group(param_group)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
