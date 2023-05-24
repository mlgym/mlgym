
from bert_lm_blueprint import BERTLMBluePrint
from ml_gym.cmd_entrypoint.cmd import get_args, run


if __name__ == '__main__':

    blueprint_class = BERTLMBluePrint
    config_path = get_args()
    run(blueprint_class=blueprint_class, run_configuration_file_path=config_path)
