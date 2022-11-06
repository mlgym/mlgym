from fastapi import FastAPI
from fastapi import status, HTTPException
from fastapi.responses import StreamingResponse
from ml_board.backend.restful_api.data_access import DataAccessIF
from ml_gym.error_handling.exception import InvalidPathError
from ml_board.backend.restful_api.data_models import RawTextFile, CheckpointResource
from typing import Callable
# from fastapi.staticfiles import StaticFiles


class RestfulAPIServer:
    def __init__(self, data_access: DataAccessIF):
        self.app = FastAPI(port=8080)
        self.data_access = data_access
        self.app.add_api_route(path="/grid_searches/{grid_search_id}/experiments",
                               methods=["GET"], endpoint=self.get_experiment_statuses)
        self.app.add_api_route(path="/grid_searches/{grid_search_id}/{config_name}",
                               methods=["PUT"], endpoint=self.add_raw_config_to_grid_search)
        self.app.add_api_route(path="/grid_searches/{grid_search_id}/{experiment_id}/{config_name}",
                               methods=["PUT"], endpoint=self.add_config_to_experiment)
        self.app.add_api_route(path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}/{checkpoint_resource}",
                               methods=["GET"], endpoint=self.get_checkpoint_resource)
        self.app.add_api_route(path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}",
                               methods=["GET"], endpoint=self.get_checkpoint_dict_epoch)

        # self.app.mount("/", StaticFiles(directory="/home/mluebberin/repositories/github/private_workspace/mlgym/src/ml_board/frontend/dashboard/build/", html=True), name="static")

    def get_experiment_statuses(self, grid_search_id: str):
        try:
            experiment_statuses = self.data_access.get_experiment_statuses(grid_search_id)
            return experiment_statuses
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Provided invalid grid_search_id {grid_search_id}') from e

    # @app.get('/grid_searches/{grid_search_id}/gs_config')
    # def get_grid_search_config(grid_search_id: str):
    #     requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), "gs_config.yml"))

    #     if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
    #         return YAMLConfigLoader.load(requested_full_path)

    #     else:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                             detail=f'Provided unsafe filepath {requested_full_path}')

    def add_raw_config_to_grid_search(self, grid_search_id: str, config_name: str, config_file: RawTextFile):
        try:
            self.data_access.add_raw_config_to_grid_search(grid_search_id=grid_search_id,
                                                           config_name=config_name,
                                                           config_file=config_file)
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Provided invalid grid_search_id {grid_search_id} or config_name {config_name}') from e

    def get_raw_config_of_grid_search(self, grid_search_id: str, config_name: str):
        raise NotImplementedError

    def add_config_to_experiment(self, grid_search_id: str, experiment_id: str, config_name: str, config: RawTextFile):
        try:
            self.data_access.add_config_to_experiment(grid_search_id=grid_search_id,
                                                      experiment_id=experiment_id,
                                                      config_name=config_name,
                                                      config=config)
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Provided invalid grid_search_id {grid_search_id}, experiment_id {experiment_id} or config_name {config_name}') from e

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource):
        try:
            file_generator = self.data_access.get_checkpoint_resource(grid_search_id=grid_search_id,
                                                                      experiment_id=experiment_id,
                                                                      epoch=epoch,
                                                                      checkpoint_resource=checkpoint_resource)
            response = StreamingResponse(file_generator, media_type="application/octet-stream")
            return response
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Provided invalid parameters for checkpoint resource.") from e

    def get_checkpoint_dict_epoch(self, grid_search_id: str, experiment_id: str, epoch: str):
        try:
            checkpoint_list = self.data_access.get_checkpoint_dict_epoch(grid_search_id=grid_search_id,
                                                                         experiment_id=experiment_id,
                                                                         epoch=epoch)
            return checkpoint_list
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Provided invalid grid_search_id {grid_search_id}, experiment_id {experiment_id} or epoch {epoch}') from e

    def run_server(self, application_server_callable: Callable):
        application_server_callable(app=self.app)
