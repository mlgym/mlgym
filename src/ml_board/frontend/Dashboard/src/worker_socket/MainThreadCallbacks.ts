import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData, { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// Note: I don't like having anything here other than the callbacks but it is what it is :')
// ========================= variables ============================//
// to check for metric and loss headers
const metric_loss_header: string[] = [];
// TODO: temporary until the mystery why this is even used be solved
const initialStateForGraphs: evalResultCustomData = {
    grid_search_id: null,
    experiments: {},
    colors_mapped_to_exp_id: {}
};


// ========================= Callbacks to update the MainThread ============================//
// ========================= MTCb == MainThreadCallback ====================================//

export const updateMTCb = (parsedSocketData: DataFromSocket) => {
    const eventType = parsedSocketData.event_type.toLowerCase();
    const dataToRedux: DataToRedux = {};
    switch (eventType) {
        case MLGYM_EVENT.JOB_STATUS:
            // dataToRedux.jobStatusData = handleJobStatusData(parsedSocketData.payload);
            dataToRedux.tableData = handleJobStatusData(parsedSocketData.payload);
            break;
        case MLGYM_EVENT.JOB_SCHEDULED:
            console.log("Job scheduled found")
            break;
        case MLGYM_EVENT.EVALUATION_RESULT:
            // TODO: get the "latest_split_metric" in the experimentsSlice too
            dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, parsedSocketData.payload as unknown as EvaluationResultPayload);
            // just save the value directly in the Experiment, since the table is being formed from there
            // later decide if the column names are going to stay hard coded or inducted from the incoming messages 
            const evalResPayload = parsedSocketData.payload as unknown as EvaluationResultPayload;
            dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, evalResPayload);
            dataToRedux.latest_split_metric = evalResPayload;
            break;
        case MLGYM_EVENT.EXPERIMENT_CONFIG:
            console.log("Exp config found")
            break;
        case MLGYM_EVENT.EXPERIMENT_STATUS:
            // dataToRedux.experimentStatusData = handleExperimentStatusData(parsedSocketData.payload);
            dataToRedux.tableData = handleExperimentStatusData(parsedSocketData.payload);
            break;
        default: throw new Error(MLGYM_EVENT.UNKNOWN_EVENT);
    }
    // this is sent as a reply ONLY AFTER the first time
    postMessage(dataToRedux);
};

export const pingMTCb = (ping: number) => {
    postMessage({ status: { ping } } as DataToRedux);
};

export const connectionMTCb = (isSocketConnected: boolean) => {
    postMessage({ status: { isSocketConnected } } as DataToRedux);
};

export const msgCounterIncMTCb = () => {
    postMessage({ status: "msg_count_increment" } as DataToRedux);
};

export const throughputMTCb = (throughput: number) => {
    postMessage({ status: { throughput } } as DataToRedux);
};
// ========================= helper methods ============================//
// if the header doesn't exist push it before returning if it was already there or not.
const check_if_header_exist = (header: string) => {
    const condition = metric_loss_header.includes(header);
    if(!condition) metric_loss_header.push(header);
    return condition;
};