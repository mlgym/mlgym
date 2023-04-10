const GRID_SEARCH_BASE_URL = "/grid_searches/<grid_search_id>";
const CHECKPOINT_BASE_URL = "/checkpoints/<grid_search_id>/<experiment_id>/<checkpoint_id>";

let api = {
    // following API to PUT config file for the whole grid search
    gridsearch_config_file: GRID_SEARCH_BASE_URL + "/<config_file_name>",

    // following API to PUT config file for a selected experiment
    experiment_config_file: GRID_SEARCH_BASE_URL + "/<experiment_id>/<config_file_name>",

    // following API to get all the experiments of a grid search
    experiments: GRID_SEARCH_BASE_URL + "/experiments",

    // following API to GET all data of a selected checkpoint
    checkpoint_url: CHECKPOINT_BASE_URL,
    
    // following APIs to GET, POST & DELETE data individually for checkpoints
    checkpoint_model: CHECKPOINT_BASE_URL + "/model",
    checkpoint_optimizer: CHECKPOINT_BASE_URL + "/optimizer",
    checkpoint_stateful_component: CHECKPOINT_BASE_URL + "/stateful_component",
    checkpoint_lr_scheduler: CHECKPOINT_BASE_URL + "/lr_scheduler"
}

export default api;