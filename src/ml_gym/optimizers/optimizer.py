from torch.optim.optimizer import Optimizer
from functools import partial
from typing import Dict, Any


class OptimizerAdapter(object):

    def __init__(self, optimizer_partial: partial):
        self.optimizer_partial = optimizer_partial
        self.optimizer: Optimizer = None

    def register_model_params(self, params):
        self.optimizer = self.optimizer_partial(params=params)

    def __getstate__(self):
        return self.optimizer.__getstate__()

    def __setstate__(self, state):
        self.optimizer.__setstate__(state)

    def __repr__(self):
        return self.optimizer.__repr__()

    def _hook_for_profile(self):
        self.optimizer._hook_for_profile()

    def state_dict(self) -> Dict[str, Any]:
        return self.optimizer.state_dict()

    def load_state_dict(self, state_dict):
        self.optimizer.load_state_dict(state_dict)

    def zero_grad(self, set_to_none: bool = False):
        self.optimizer.zero_grad(set_to_none)

    def step(self, closure=None):
        self.optimizer.step(closure)

    def add_param_group(self, param_group):
        self.optimizer.add_param_group(param_group)
