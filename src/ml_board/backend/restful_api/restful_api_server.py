import base64
from fastapi import FastAPI, File
from fastapi import status, HTTPException
from fastapi.responses import StreamingResponse
from ml_board.backend.restful_api.data_access import DataAccessIF
from ml_gym.error_handling.exception import InvalidPathError, SystemInfoFetchError
from ml_board.backend.restful_api.data_models import FileFormat, RawTextFile, CheckpointResource
from typing import Callable
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.staticfiles import StaticFiles


class RestfulAPIServer:
    """
    RestAPI Server class

    Creates FastAPI Server Object with HTTP RestAPIs for grid search and checkpoint communication.
    """

    def __init__(self, data_access: DataAccessIF):
        self.app = FastAPI(port=8080)
        origins = ["*"]
        self.app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )
        self.data_access = data_access
        self.app.add_api_route(path="/grid_searches/{grid_search_id}/experiments", methods=["GET"], endpoint=self.get_experiment_statuses)
        self.app.add_api_route(
            path="/grid_searches/{grid_search_id}/{experiment_id}/{config_name}", methods=["GET"], endpoint=self.get_experiment_config
        )
        self.app.add_api_route(path="/grid_searches/{grid_search_id}/{config_name}", methods=["GET"], endpoint=self.get_grid_config)
        self.app.add_api_route(
            path="/grid_searches/{grid_search_id}/{config_name}", methods=["PUT"], endpoint=self.add_raw_config_to_grid_search
        )
        self.app.add_api_route(
            path="/grid_searches/{grid_search_id}/{experiment_id}/{config_name}", methods=["PUT"], endpoint=self.add_config_to_experiment
        )
        self.app.add_api_route(
            path="/checkpoint_list/{grid_search_id}/{experiment_id}",
            methods=["GET"],
            endpoint=self.get_checkpoint_list,
        )
        self.app.add_api_route(
            path="/checkpoint_list/{grid_search_id}/{experiment_id}/{epoch}", methods=["GET"], endpoint=self.get_checkpoint_dict_epoch
        )
        self.app.add_api_route(
            path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}/{checkpoint_resource}",
            methods=["GET"],
            endpoint=self.get_checkpoint_resource,
        )
        self.app.add_api_route(
            path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}/{checkpoint_resource}",
            methods=["POST"],
            endpoint=self.add_checkpoint_resource,
        )
        self.app.add_api_route(
            path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}",
            methods=["DELETE"],
            endpoint=self.delete_checkpoints,
        )
        self.app.add_api_route(
            path="/checkpoints/{grid_search_id}/{experiment_id}/{epoch}/{checkpoint_resource}",
            methods=["DELETE"],
            endpoint=self.delete_checkpoint_resource,
        )
        self.app.add_api_route(
            path="/system-info/{grid_search_id}/{experiment_id}",
            methods=["GET"],
            endpoint=self.get_system_info,
        )

        # self.app.mount("/", StaticFiles(directory="/home/mluebberin/repositories/github/private_workspace/mlgym/src/ml_board/frontend/dashboard/build/", html=True), name="static")

    def get_experiment_statuses(self, grid_search_id: str):
        """
        ``HTTP GET`` Experiment Status for a Grid Search ID.

        :params:
             grid_search_id (str): Grid Search ID

        :returns: JSON object - experiment_statuses
        """
        try:
            experiment_statuses = self.data_access.get_experiment_statuses(grid_search_id)
            return experiment_statuses
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Provided invalid grid_search_id {grid_search_id}") from e

    def get_experiment_config(self, grid_search_id: str, experiment_id: str, config_name: str):
        """
        ``HTTP GET`` Fetch specific experiment config
          given the experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             config_name (str): Name of Configuration file

        :returns: JSON stream response
        """
        try:
            file_generator = self.data_access.get_experiment_config(
                grid_search_id=grid_search_id, experiment_id=experiment_id, config_name=config_name
            )
            response = StreamingResponse(file_generator, media_type="application/json")
            return response
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Provided invalid grid_search_id {grid_search_id}") from e

    def get_grid_config(self, grid_search_id: str, config_name: str):
        """
        ``HTTP GET`` Fetch grid config for a Grid Search ID.

        :params:
             grid_search_id (str): Grid Search ID
             config_name (str): Name of Configuration file

        :returns: YML stream response
        """
        try:
            file_generator = self.data_access.get_grid_config(grid_search_id=grid_search_id, config_name=config_name)
            response = StreamingResponse(file_generator, media_type="application/yml")
            return response
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Provided invalid grid_search_id {grid_search_id}") from e

    # @app.get('/grid_searches/{grid_search_id}/gs_config')
    # def get_grid_search_config(grid_search_id: str):
    #     requested_full_path = os.path.realpath(os.path.join(top_level_logging_path, str(grid_search_id), "gs_config.yml"))

    #     if is_safe_path(base_dir=top_level_logging_path, requested_path=requested_full_path):
    #         return YAMLConfigLoader.load(requested_full_path)

    #     else:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                             detail=f'Provided unsafe filepath {requested_full_path}')

    def add_raw_config_to_grid_search(self, grid_search_id: str, config_name: str, config_file: RawTextFile):
        """
        ``HTTP PUT`` Add Config for a Grid Search ID

        :params:
             grid_search_id (str): Grid Search ID
             config_name (str): Name of Configuration file
             config_file (RawTextFile) : RawTextFile Object

        """
        try:
            self.data_access.add_raw_config_to_grid_search(grid_search_id=grid_search_id, config_name=config_name, config_file=config_file)
        except InvalidPathError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provided invalid grid_search_id {grid_search_id} or config_name {config_name}",
            ) from e

    def add_config_to_experiment(self, grid_search_id: str, experiment_id: str, config_name: str, config: RawTextFile):
        """
        ``HTTP PUT`` Add specific experiment config
          given the experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             config_name (str): Name of Configuration file
             config (RawTextFile) : RawTextFile Object

        """
        try:
            self.data_access.add_config_to_experiment(
                grid_search_id=grid_search_id, experiment_id=experiment_id, config_name=config_name, config=config
            )
        except InvalidPathError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provided invalid grid_search_id {grid_search_id}, experiment_id {experiment_id} or config_name {config_name}",
            ) from e

    def get_checkpoint_dict_epoch(self, grid_search_id: str, experiment_id: str, epoch: str):
        """
        ``HTTP GET`` Fetch all checkpoint resource pickle files
          given the epoch, experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (str): Epoch number

        :returns: List of Checkpoints
        """
        try:
            checkpoint_list = self.data_access.get_checkpoint_dict_epoch(
                grid_search_id=grid_search_id, experiment_id=experiment_id, epoch=epoch
            )
            return checkpoint_list
        except InvalidPathError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provided invalid grid_search_id {grid_search_id}, experiment_id {experiment_id} or epoch {epoch}",
            ) from e

    def get_checkpoint_list(self, grid_search_id: str, experiment_id: str):
        """
        ``HTTP GET`` Fetch all checkpoint resource pickle files
          given the epoch, experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID

        :returns: List of checkpoints
        """
        try:
            checkpoint_list = self.data_access.get_checkpoint_list(grid_search_id=grid_search_id, experiment_id=experiment_id)
            return checkpoint_list
        except InvalidPathError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Provided invalid parameters for fetching checkpoint list."
            ) from e

    def get_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource):
        """
        ``HTTP GET`` Fetch checkpoint resource pickle file
          given the experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (str): Epoch number
             checkpoint_resource (CheckpointResource) : CheckpointResource type

        :returns: Pickle file Stream response
        """
        try:
            file_generator = self.data_access.get_checkpoint_resource(
                grid_search_id=grid_search_id, experiment_id=experiment_id, epoch=epoch, checkpoint_resource=checkpoint_resource
            )
            response = StreamingResponse(file_generator, media_type="application/octet-stream")
            return response
        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Provided invalid parameters for checkpoint resource.") from e

    def delete_checkpoint_resource(self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource):
        """
        ``HTTP DELETE`` Delete checkpoint resource pickle file
          given the epoch, experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (str): Epoch number
             checkpoint_resource (CheckpointResource) : CheckpointResource type
        """
        try:
            self.data_access.delete_checkpoint_resource(
                grid_search_id=grid_search_id, experiment_id=experiment_id, epoch=epoch, checkpoint_resource=checkpoint_resource
            )

        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Provided invalid parameters for checkpoint resource.") from e

    def delete_checkpoints(self, grid_search_id: str, experiment_id: str, epoch: str):
        """
        ``HTTP DELETE`` Delete checkpoint resource pickle file
          given the epoch, experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (str): Epoch number
        """
        try:
            self.data_access.delete_checkpoints(grid_search_id=grid_search_id, experiment_id=experiment_id, epoch=epoch)

        except InvalidPathError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Provided invalid parameters for checkpoint resource.") from e

    def add_checkpoint_resource(
        self, grid_search_id: str, experiment_id: str, epoch: str, checkpoint_resource: CheckpointResource, file: bytes = File(...)
    ):
        """
        ``HTTP POST`` Add a checkpoint resource pickle file
          given the epoch, experiment ID & grid search ID.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             epoch (str): Epoch number
             checkpoint_resource (CheckpointResource) : CheckpointResource type
             file (bytes): Pickle file to be added

        :returns: Pickle file Stream response
        """
        try:
            payload_pickle = base64.b64decode(file)
            self.data_access.add_checkpoint_resource(
                grid_search_id=grid_search_id,
                experiment_id=experiment_id,
                epoch=epoch,
                checkpoint_resource=checkpoint_resource,
                payload_pickle=payload_pickle,
            )
        except InvalidPathError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provided invalid payload or grid_search_id {grid_search_id}, experiment_id {experiment_id} or epoch {epoch}.",
            ) from e
    
    def get_system_info(self, grid_search_id: str, experiment_id: str):
        """
        ``HTTP GET`` Fetch System Information for model card.

        :params:
             grid_search_id (str): Grid Search ID
             experiment_id (str): Experiment ID
             config_name (str): Name of Configuration file

        :returns: JSON object - System Information of host machine (CPU & GPU)
        """
        try:
            file_generator = self.data_access.get_experiment_config(
                grid_search_id=grid_search_id, experiment_id=experiment_id, config_name="system_info"
            )
            response = StreamingResponse(file_generator, media_type="application/json")
            return response
        except SystemInfoFetchError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Error while fetching server system information") from e

    def run_server(self, application_server_callable: Callable):
        application_server_callable(app=self.app)
