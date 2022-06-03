from enum import Enum


class ValidationMode(Enum):
    NESTED_CV = "nested_cv"
    CROSS_VALIDATION = "cross_validation"
    GRID_SEARCH = "grid_search"


class RunMode(Enum):
    TRAIN = "train"
    RE_EVAL = "re_eval"
    WARM_START = "warm_start"
