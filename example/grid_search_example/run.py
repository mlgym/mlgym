from ml_gym.cmd_entrypoint.cmd import get_args, run
from conv_net_blueprint import ConvNetBluePrint

if __name__ == '__main__':

    blueprint_class = ConvNetBluePrint
    run_configuration_file_path = get_args()
    run(blueprint_class=blueprint_class, run_configuration_file_path=run_configuration_file_path)
