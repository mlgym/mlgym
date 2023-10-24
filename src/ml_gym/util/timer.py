import torch.distributed as dist
from functools import wraps
import time

import logging
logging.basicConfig(filename='icde_2024_experiments.log', encoding='utf-8', level=logging.DEBUG)


def timeit_ns(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        print(
            f'Function {func.__name__} Took {(total_time/1000000000):.4f} seconds')
        return result
    return timeit_wrapper


class NSTimer(object):

    def __init__(self, key: str) -> None:
        self.key = key

    def __enter__(self):
        self.start()

    def start(self):
        self.start_time = time.perf_counter_ns()

    def __exit__(self, *args):
        self.stop()

    def stop(self):
        end_time = time.perf_counter_ns()
        if dist.is_available() and dist.is_initialized():
            rank = dist.get_rank()
        else:
            rank = 0

        message = {"rank": rank, "key": self.key, "duration": (
            end_time - self.start_time) / 1000000000}
        logging.debug(message)
