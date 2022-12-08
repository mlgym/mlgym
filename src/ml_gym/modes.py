from enum import Enum


class ValidationMode(Enum):
    NESTED_CV = "NESTED_CROSS_VALIDATION"
    CROSS_VALIDATION = "CROSS_VALIDATION"
    GRID_SEARCH = "GRID_SEARCH"


class RunMode(Enum):
    TRAIN = "train"
    # RE_EVAL = "re_eval"
    WARM_START = "warm_start"
