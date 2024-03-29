export const defaultGridSearchConfigFileName = "grid_search_config";
export const defaultExperimentConfigFileName = "experiment_config";
export const defaultRunConfigFileName = "run_config";

const GRID_SEARCH_BASE_URL = "/grid_searches/<grid_search_id>";
const CHECKPOINT_BASE_URL = "/checkpoints/<grid_search_id>/<experiment_id>/<checkpoint_id>";
const CHECKPOINT_LIST_BASE_URL = "/checkpoint_list/<grid_search_id>/<experiment_id>";
const MODEL_CARDS_BASE_URL = "/model-card/<grid_search_id>";

export default {
    // following API to GET config file for the whole grid search
    gridsearch_config_file: GRID_SEARCH_BASE_URL + "/" + defaultGridSearchConfigFileName,

    // following API to GET config file for the grid search run
    run_config_file: GRID_SEARCH_BASE_URL + "/" + defaultRunConfigFileName,
    
    // following API to PUT config file for a selected experiment
    experiment_config_file: GRID_SEARCH_BASE_URL + "/<experiment_id>/" + defaultExperimentConfigFileName,

    // following API to get all the experiments of a grid search
    experiments: GRID_SEARCH_BASE_URL + "/experiments",

    // following API to GET data of all checkpoints of a selected experiment
    checkpoint_list: CHECKPOINT_LIST_BASE_URL,

    // following API to GET all data of a selected checkpoint
    selected_checkpoint_list: CHECKPOINT_LIST_BASE_URL + "/<checkpoint_id>",
    
    // following APIs to GET, POST & DELETE data individually for checkpoints
    // <checkpoint_resource> can be: model, optimizer, stateful_component, lr_scheduler
    checkpoint_resource: CHECKPOINT_BASE_URL + "/<checkpoint_resource>",

    // following API to GET system details like CPU & GPU for model card
    model_card_sys_info: MODEL_CARDS_BASE_URL + "/<experiment_id>",
};