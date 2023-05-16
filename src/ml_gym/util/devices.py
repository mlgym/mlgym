import torch
import os
from typing import List

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"


def get_devices(gpu_device_ids: List[int] = None) -> List[torch.device]:
    if gpu_device_ids is None:
        print("WARNING: No cuda devices specified. Falling back to CPUs.")   # TODO Introduce proper logging...
        return [torch.device("cpu")]
    if torch.cuda.is_available():  # if we got some GPUs
        return [torch.device(f"cuda:{device_id}") for device_id in gpu_device_ids]
    else:
        print("WARNING: No cuda devices available. Falling back to CPUs.")   # TODO Introduce proper logging...
        return [torch.device("cpu")]


if __name__ == "__main__":
    print(get_devices())
