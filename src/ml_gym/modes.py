from enum import Enum


class ValidationMode(Enum):
    NESTED_CV = "NESTED_CROSS_VALIDATION"
    CROSS_VALIDATION = "CROSS_VALIDATION"
    GRID_SEARCH = "GRID_SEARCH"


class RunMode(Enum):
    TRAIN = "train"
    WARM_START = "warm_start"


class ParallelizationMode(Enum):

    PARALLEL_GS_SINGLE_NODE_MULTI_GPU = "PARALLEL_GS_SINGLE_NODE_MULTI_GPU"
    SEQUENTIAL_GS_SINGLE_NODE_DISTRIBUTED = "SEQUENTIAL_GS_SINGLE_NODE_DISTRIBUTED"
