import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData, { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// Note: I don't like having anything here other than the callbacks but it is what it is :')
// ========================= variables ============================//
// TODO: in #145 #147 this has been done with out the need of this, check if still needed (check the TODO drafts)
// to check for metric and loss headers
const metric_loss_header: string[] = [];
// TODO: temporary until the mystery why this is even used be solved
const initialStateForGraphs: evalResultCustomData = {
    grid_search_id: null,
    experiments: {},
    colors_mapped_to_exp_id: {}
};

// Hashing is faster instead of switching over the the eventType
const MapEventToProcess = {
    [MLGYM_EVENT.JOB_STATUS]: (dataToRedux: DataToRedux, data: any) => { dataToRedux.tableData = handleJobStatusData(data) },
    [MLGYM_EVENT.JOB_SCHEDULED]: () => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (dataToRedux: DataToRedux, data: any) => {
        const evalResPayload = data as unknown as EvaluationResultPayload;
        dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, evalResPayload);
        dataToRedux.latest_split_metric = evalResPayload;
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: () => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: any) => { dataToRedux.tableData = handleExperimentStatusData(data) },
};

const BUFFER_WINDOW_LIMIT_IN_SECONDS = 30;
let bufferWindow = 0;

setInterval(() => {
    bufferWindow++;

    if (bufferWindow >= BUFFER_WINDOW_LIMIT_IN_SECONDS) {
        bufferWindow = 0
    }
}, 1000);

// ========================= Callbacks to update the MainThread ============================//
let bufferQueue: Array<DataToRedux> = [];

export const updateMainThreadCallback = (parsedSocketData: DataFromSocket) => {
    const eventType = parsedSocketData.event_type.toLowerCase();
    const dataToRedux: DataToRedux = {};
    
    MapEventToProcess[eventType as keyof typeof MapEventToProcess](dataToRedux, parsedSocketData.payload);

    // this is sent as a reply ONLY AFTER the first time
    bufferQueue.push(dataToRedux);

    if (bufferQueue.length > 0  && (bufferQueue.length >= 1000 || bufferWindow === 0)) {
        postMessage(bufferQueue);
        bufferQueue = [];
    }
};

export const pingMainThreadCallback = (ping: number) => {
    postMessage([{ status: { ping } }]);
};

export const connectionMainThreadCallback = (isSocketConnected: boolean) => {
    postMessage([{ status: { isSocketConnected } }]);
};

export const msgCounterIncMainThreadCallback = () => {
    postMessage([{ status: "msg_count_increment" }]);
};

export const throughputMainThreadCallback = (throughput: number) => {
    postMessage([{ status: { throughput } }]);
};

// ========================= helper methods ============================//
// if the header doesn't exist push it before returning if it was already there or not.
const check_if_header_exist = (header: string) => {
    const condition = metric_loss_header.includes(header);
    if(!condition) metric_loss_header.push(header);
    return condition;
};