from gpt2_blueprint import GPT2LLMBluePrint
from ml_gym.cmd_entrypoint.cmd import get_args, run


if __name__ == '__main__':

    blueprint_class = GPT2LLMBluePrint
    config_path = get_args()
    run(blueprint_class=blueprint_class, run_configuration_file_path=config_path)