from ml_gym.blueprints.blue_prints import BluePrint
import numpy as np
import torch


def mocked_sum(blueprint: BluePrint, arr, device):
    arr = torch.tensor(np.array(arr), device=device)
    s = 0
    for i in arr:
        s += i
    return s
