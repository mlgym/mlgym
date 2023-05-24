from ml_gym.checkpointing.checkpointing import SaveLastEpochOnlyCheckpointingStrategy, SaveAllCheckpointingStrategy, Checkpointing,\
    CheckpointingIF


class CheckpointingStrategyFactory:
    """
    Checkpointing Stratergy Class used for finding what stratergy to use for 
    creating checkpoints for the experiments while running MlGym Job.
    """
    @staticmethod
    def get_save_last_epoch_only_checkpointing_strategy() -> CheckpointingIF:
        strategy = SaveLastEpochOnlyCheckpointingStrategy()
        return Checkpointing(checkpointing_strategy=strategy)

    @staticmethod
    def get_save_all_checkpointing_strategy() -> CheckpointingIF:
        strategy = SaveAllCheckpointingStrategy()
        return Checkpointing(checkpointing_strategy=strategy)
