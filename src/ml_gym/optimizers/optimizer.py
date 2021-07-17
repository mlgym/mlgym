from torch.optim.optimizer import Optimizer
from functools import partial
from typing import Dict, Any
from copy import deepcopy


class OptimizerAdapter(object):

    def __init__(self, optimizer_partial: partial):
        self._optimizer_partial = optimizer_partial
        self._optimizer: Optimizer = None

    def register_model_params(self, params):
        self._optimizer = self._optimizer_partial(params=params)

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
        return self._optimizer.state_dict()

    def load_state_dict(self, state_dict):
        self._optimizer.load_state_dict(state_dict)

    def zero_grad(self, set_to_none: bool = False):
        self._optimizer.zero_grad(set_to_none)

    def step(self, closure=None):
        self._optimizer.step(closure)

    def add_param_group(self, param_group):
        self._optimizer.add_param_group(param_group)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result