from numpy import save
from ml_gym.checkpoint.checkpoint import DefaultCheckpoint, RegularIntervalCheckpoint, LastCheckpoint, BestMetricCheckpoint
from typing import Callable, Dict, Any, List

class CheckpointFactory:
    @staticmethod
    def get_default_checkpoint(tag: str, save_weights_only: bool = False):
        checkpoint_result = DefaultCheckpoint(tag = tag, identifier = " DEFAULT", save_weights_only = save_weights_only)
        return checkpoint_result
    
    @staticmethod 
    def get_regular_interval_checkpoint(tag: str, checkpoint_interval: int, save_weights_only: bool = False):
        checkpoint_result = RegularIntervalCheckpoint(tag = tag, 
                                                      identifier = "REGULAR_INTERVAL", 
                                                      save_weights_only = save_weights_only, 
                                                      checkpoint_interval = checkpoint_interval)
        return checkpoint_result

    @staticmethod 
    def get_last_checkpoint(tag: str, save_weights_only: bool = False):
        checkpoint_result = LastCheckpoint(tag = tag, identifier = "LAST", save_last_only = save_weights_only)
        return checkpoint_result
    
    @staticmethod
    def get_best_metric_checkpoint(tag: str, inference_metric: str, mode: str = None, best_count: int =1, save_weights_only: bool = False):
        checkpoint_result = BestMetricCheckpoint(tag = tag, 
                                                idenitifier = "BEST_METRIC",
                                                inference_metric = inference_metric,
                                                mode = mode,
                                                best_count = best_count,
                                                save_weights_only = save_weights_only)

    


