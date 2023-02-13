
from bert_lm_blueprint import BERTLMBluePrint
from ml_gym.cmd_entrypoint.cmd import get_args, run


if __name__ == '__main__':

    blueprint_class = BERTLMBluePrint
    fun, args = get_args()
    run(fun=fun, blueprint_class=blueprint_class, args=args)
