from typing import List
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.batching.batch import EvaluationBatchResult
from abc import abstractmethod
from dataclasses import dataclass, field


@dataclass
class CheckpointingInstruction:
    save_current: bool = False
    checkpoints_to_delete: List[int] = field(default_factory=list)


class CheckpointingIF(StatefulComponent):
    @abstractmethod
    def get_model_checkpoint_instruction(self, current_epoch: int, num_epochs: int,
                                         evaluation_result: EvaluationBatchResult) -> CheckpointingInstruction:
        raise NotImplementedError


class Checkpointing(CheckpointingIF):
    def __init__(self, checkpointing_strategy: CheckpointingIF):
        self.checkpointing_strategy = checkpointing_strategy

    def get_model_checkpoint_instruction(self, current_epoch: int, num_epochs: int,
                                         evaluation_result: EvaluationBatchResult) -> CheckpointingInstruction:
        return self.checkpointing_strategy.get_model_checkpoint_instruction(current_epoch=current_epoch, num_epochs=num_epochs,
                                                                            evaluation_result=evaluation_result)


class SaveLastEpochOnlyCheckpointingStrategy(CheckpointingIF):
    def __init__(self):
        pass

    def get_model_checkpoint_instruction(self, current_epoch: int, num_epochs: int,
                                         evaluation_result: EvaluationBatchResult) -> CheckpointingInstruction:
        return CheckpointingInstruction(save_current=True, checkpoints_to_delete=[current_epoch-1])


class SaveAllCheckpointingStrategy(CheckpointingIF):
    def __init__(self):
        pass

    def get_model_checkpoint_instruction(self, current_epoch: int, num_epochs: int,
                                         evaluation_result: EvaluationBatchResult) -> CheckpointingInstruction:
        return CheckpointingInstruction(save_current=True, checkpoints_to_delete=[])

# class RegularIntervalCheckpoint(Checkpointing):
#     def __init__(self,  tag: str, identifier: str,
#                  save_weights_only: Optional[bool] = False,
#                  checkpoint_interval: Optional[int] = None,
#                  save_last: bool = True):
#         super().__init__(tag=tag, identifier=identifier, save_weights_only=save_weights_only)
#         self.checkpoint_interval = checkpoint_interval
#         self.save_last = save_last

#     def model_checkpoint(self, current_epoch: int, num_epochs: int, evaluation_result: EvaluationBatchResult) -> Dict:
#         checkpoint_result = {'checkpoint_save': None,
#                              'checkpoint_delete': None}
#         if current_epoch == num_epochs:
#             if self.save_last:
#                 checkpoint_result['checkpoint_save'] = current_epoch
#         elif current_epoch % self.checkpoint_interval == 0:
#             checkpoint_result['checkpoint_save'] = current_epoch
#         self.checkpoint_history['epoch_' + str(current_epoch)] = checkpoint_result
#         return checkpoint_result


# class LastCheckpoint(Checkpointing):
#     def __init__(self,  tag: str, identifier: str,
#                  save_weights_only: Optional[bool] = False,
#                  save_last_only: bool = True
#                  ):
#         super().__init__(tag=tag, identifier=identifier, save_weights_only=save_weights_only)
#         self.save_last_only = save_last_only

#     def model_checkpoint(self,
#                          current_epoch: int,
#                          num_epochs: int) -> bool:
#         checkpoint_result = {'checkpoint_save': None,
#                              'checkpoint_delete': None}
#         if current_epoch == num_epochs:
#             checkpoint_result['checkpoint_save'] = current_epoch
#         self.checkpoint_history['epoch_' + str(current_epoch)] = checkpoint_result
#         return checkpoint_result


# class BestMetricCheckpoint(Checkpointing):
#     def __init__(self,  tag: str, identifier: str,
#                  inference_metric: str,
#                  mode: Optional[str] = None,
#                  best_count: int = 1,
#                  save_weights_only: Optional[bool] = False,

#                  ):
#         super().__init__(tag=tag, identifier=identifier, save_weights_only=save_weights_only)
#         self.mode = mode
#         self.inference_metric = inference_metric
#         self.best_count = best_count
#         self.best_metrics = {}

#     def model_checkpoint(self, current_epoch: int, num_epochs: int, evaluation_result: EvaluationBatchResult) -> Dict:

#         if not self.mode:
#             self.initialize_mode(evaluation_result=evaluation_result)
#         checkpoint_result = self.compare_best_metrics(current_epoch, evaluation_result)
#         self.checkpoint_history['epoch_' + str(current_epoch)] = checkpoint_result
#         return checkpoint_result

#     def compare_best_metrics(self, current_epoch: int, evaluation_result: EvaluationBatchResult) -> Dict:
#         checkpoint_result = {'checkpoint_save': None,
#                              'checkpoint_delete': None}
#         current_metric = self.get_current_metric(current_epoch, evaluation_result)
#         if len(self.best_metrics) < self.best_count:
#             self.best_metrics[current_epoch] = current_metric
#             checkpoint_result['checkpoint_save'] = current_epoch
#         else:
#             compare_fn = max if self.mode == "min" else min
#             best_item_key = compare_fn(self.best_metrics)
#             if compare_fn(self.best_metrics[best_item_key], current_metric) == current_metric:
#                 self.best_metrics.pop(best_item_key)
#                 self.best_metrics[current_epoch] = current_metric
#                 checkpoint_result['checkpoint_save'] = current_epoch
#                 checkpoint_result['checkpoint_delete'] = best_item_key

#         return checkpoint_result

#     def get_current_metric(self, current_epoch: int, evaluation_result: EvaluationBatchResult) -> float:
#         if self.inference_metric in evaluation_result.losses.keys():
#             current_metric = evaluation_result.losses[self.inference_metric][current_epoch]
#         elif self.inference_metric in evaluation_result.metrics.keys():
#             current_metric = evaluation_result.metrics[self.inference_metric][current_epoch]
#         else:
#             raise RuntimeError("{} not present in the metrics or the loss keys.".format(self.inference_metric))
#         return current_metric

#     def initialize_mode(self, evaluation_result: EvaluationBatchResult):
#         if not self.mode:
#             # set up min-max mode based on the metric type if not specified by the user
#             if self.inference_metric in evaluation_result.losses.keys():
#                 self.mode = "min"
#             elif self.inference_metric in evaluation_result.metrics.keys():
#                 # TODO: check if metrics are always maximized or use some better logic to set mode
#                 self.mode = "max"
#             else:
#                 raise RuntimeError("{} not present in the metrics or the loss keys.".format(self.inference_metric))
