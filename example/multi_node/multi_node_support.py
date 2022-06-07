
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.validation.gs_validator import GridSearchValidator
from conv_net_blueprint import ConvNetBluePrint
import deepspeed


if __name__ == "__main__":
    gs_config_path = "/home/mluebberin/repositories/github/private_workspace/mlgym/example/grid_search/single_model_config.yml"
    dashify_logging_path = "/home/mluebberin/repositories/github/private_workspace/mlgym/dashify_logging"
    gs_config = YAMLConfigLoader.load(gs_config_path)

    blueprints = GridSearchValidator(grid_search_id=0).create_blue_prints(blue_print_type=ConvNetBluePrint,
                                                                          job_type=AbstractGymJob.Type.STANDARD,
                                                                          gs_config=gs_config, num_epochs=10,
                                                                          dashify_logging_path=dashify_logging_path)
    components = blueprints[0].construct_components(component_names=["model", "data_loaders"])
    model = components["model"]
    data_loaders = components["data_loaders"]
   #  deepspeed.init_distributed()
    model_engine, optimizer, _, _ = deepspeed.initialize(#args=cmd_args,
                                                         model=model,
                                                         model_parameters=model.parameters())
