from typing import List, Dict
from enum import Enum
import os

from ml_gym.error_handling.exception import CheckpointEntityError


class CheckpointEntityTransferStatus(Enum):

    TRANSFERRING = "TRANSFERRING"
    TRANSFERRED = "TRANSFERRED"
    DELETED = "DELETED"


class CheckpointEntity:

    def __init__(self, grid_search_id: str, experiment_id: int, checkpoint_id: int, entity_id: str, final_num_chunks: int):
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id
        self.checkpoint_id = checkpoint_id
        self.entity_id = entity_id
        self._chunks: List[bytes] = [None]*final_num_chunks  # chunk_id -> bytes object

    def get_transfer_status(self) -> CheckpointEntityTransferStatus:
        if self._chunks is None:
            return CheckpointEntityTransferStatus.DELETED

        for chunk in self._chunks[::-1]:
            if chunk is None:
                return CheckpointEntityTransferStatus.TRANSFERRING

        return CheckpointEntityTransferStatus.TRANSFERRED

    def add_chunk(self, chunk_id: int, chunk_data: bytes) -> "CheckpointEntity":
        self._chunks[chunk_id] = chunk_data
        return self

    def get_chunk_list(self) -> List[bytes]:
        return self._chunks

    def delete_chunks(self):
        self._chunks = None


class CheckpointCache:

    def __init__(self):
        # grid_search_id/experiment_id/checkpoint_id (epoch)/entity_id (e.g. model) -> {chunk_id -> stream_chunk, status=<DELETED, >}
        self._checkpoint_dict: Dict[str, CheckpointEntity] = {}  # TODO make this thread-safe

    def add_chunk(self, grid_search_id: str, experiment_id: str, checkpoint_id: int, entity_id: str,
                  chunk_id: int, chunk_data: bytes, final_num_chunks: int) -> CheckpointEntity:
        full_key = os.path.join(grid_search_id, str(experiment_id), str(checkpoint_id), str(entity_id))
        if full_key not in self._checkpoint_dict:
            entity = CheckpointEntity(grid_search_id=grid_search_id,
                                      experiment_id=experiment_id,
                                      checkpoint_id=checkpoint_id,
                                      entity_id=entity_id,
                                      final_num_chunks=final_num_chunks)
            self._checkpoint_dict[full_key] = entity

        entity = self._checkpoint_dict[full_key]
        if entity.get_transfer_status() == CheckpointEntityTransferStatus.TRANSFERRING:
            entity.add_chunk(chunk_id=chunk_id, chunk_data=chunk_data)
            return entity
        else:
            raise CheckpointEntityError(f"Cannot add chunk to entitity. CheckpointEntityTransferStatus is {entity.get_transfer_status()}")

    def delete_entity(self, grid_search_id: str, experiment_id: str, checkpoint_id: int, entity_id: str,
                      chunk_id: int, chunk_data: bytes, final_num_chunks: int):

        full_key = os.path.join(grid_search_id, str(experiment_id), str(checkpoint_id), str(entity_id))
        if full_key in self._checkpoint_dict:
            entity = self._checkpoint_dict[full_key]
            entity.delete_chunks()
            print(f"Deleted {full_key}")

        else:
            raise CheckpointEntityError(f"Cannot delete checkpoint entity. Key {full_key} not present.")
