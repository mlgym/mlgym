import argparse
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable, MLgymStatusLoggerConfig, MLgymStatusLoggerTypes
from ml_gym.modes import RunMode, ValidationMode
from conv_net_blueprint import ConvNetBluePrint
from ml_gym.starter import MLGymStarter


def parse_args():
    parser = argparse.ArgumentParser(description='Run a grid search on CPUs or distributed over multiple GPUs')
    parser.add_argument('--num_epochs', type=int, help='Number of epoch', default=None)
    parser.add_argument('--validation_mode', choices=['NESTED_CV', 'GRID_SEARCH', 'CROSS_VALIDATION'], required=True)
    parser.add_argument('--run_mode', choices=['TRAIN', 'RE_EVAL', 'WARM_START'], required=True)
    parser.add_argument('--process_count', type=int, required=True, help='Max. number of processes running at a time.')
    parser.add_argument('--dashify_logging_path', type=str, required=True, help='Path to the dashify root logging directory')
    parser.add_argument('--text_logging_path', type=str, required=True, help='Path to python textual logging directory')
    parser.add_argument('--gs_config_path', type=str, required=True, help='Path to the grid search config')
    parser.add_argument('--evaluation_config_path', type=str, required=False, help='Path to the evaluation config')
    parser.add_argument('--gpus', type=int, nargs='+', help='Indices of GPUs to distribute the GS over', default=None)
    parser.add_argument('--log_std_to_file', default=False, action="store_true", help='Flag for forwarding std output to file')
    parser.add_argument('--websocket_logging_servers', type=str, nargs='+',
                        help='List of websocket logging servers, e.g., 127.0.0.1:9090 127.0.0.1:8080', default=None)
    parser.add_argument('--keep_interim_results', default=False, action="store_true",
                        help='Flag if intermediate results i.e., models, optimizer etc. states are to be stored')

    args = parser.parse_args()
    num_epochs = args.num_epochs
    validation_mode = args.validation_mode
    run_mode = args.run_mode
    dashify_logging_path = args.dashify_logging_path
    gs_config_path = args.gs_config_path
    process_count = args.process_count
    gpus = args.gpus
    text_logging_path = args.text_logging_path
    log_std_to_file = args.log_std_to_file
    evaluation_config_path = args.evaluation_config_path
    keep_interim_results = args.keep_interim_results
    websocket_logging_servers = [(f"{protocol}:{ip}", int(port)) for protocol, ip, port in [
        connection.split(":") for connection in args.websocket_logging_servers]]
    return num_epochs, validation_mode, run_mode, dashify_logging_path, text_logging_path, gs_config_path, evaluation_config_path, process_count, gpus, log_std_to_file, keep_interim_results, websocket_logging_servers


if __name__ == '__main__':
    num_epochs, validation_mode, run_mode, dashify_logging_path, text_logging_path, gs_config_path, evaluation_config_path, process_count, gpus, log_std_to_file, keep_interim_results, websocket_logging_servers = parse_args()
    logging_configs = [MLgymStatusLoggerConfig(logger_type=MLgymStatusLoggerTypes.STREAMED_LOGGER, logger_config={"host": ip, "port": port})
                       for ip, port in websocket_logging_servers]
    logger_collection_constructable = MLgymStatusLoggerCollectionConstructable(logging_configs)

    starter = MLGymStarter(blue_print_class=ConvNetBluePrint,
                           validation_mode=ValidationMode[validation_mode],
                           run_mode=RunMode[run_mode],
                           dashify_logging_path=dashify_logging_path,
                           text_logging_path=text_logging_path,
                           process_count=process_count,
                           gpus=gpus,
                           log_std_to_file=log_std_to_file,
                           gs_config_path=gs_config_path,
                           evaluation_config_path=evaluation_config_path,
                           num_epochs=num_epochs,
                           keep_interim_results=keep_interim_results,
                           logger_collection_constructable=logger_collection_constructable)
    starter.start()
