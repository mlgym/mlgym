import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData from "./event_handlers/EvaluationResultHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// ========================= variables ============================//

// Hashing is faster instead of switching over the the eventType
const MapEventToProcess: { [event: string]: (output: DataToRedux, input: JSON) => void } = {
    [MLGYM_EVENT.JOB_STATUS]: (dataToRedux: DataToRedux, data: JSON): void => { dataToRedux.tableData = handleJobStatusData(data) },
    [MLGYM_EVENT.JOB_SCHEDULED]: (dataToRedux: DataToRedux, data: JSON): void => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (dataToRedux: DataToRedux, data: JSON): void => {
        const { experiment_id, charts_updates, table_scores } = handleEvaluationResultData(data);
        dataToRedux.chartsUpdates = charts_updates;
        dataToRedux.tableData = { experiment_id, ...table_scores };
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: (dataToRedux: DataToRedux, data: JSON): void => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: JSON): void => { dataToRedux.tableData = handleExperimentStatusData(data) },
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

export const updateMainThreadCallback = (socketData: JSON) => {
    // parse data from socket then extract event_type and payload
    const { data: { event_type, payload } } = socketData as DataFromSocket;
    // place holder for redux data
    const dataToRedux: DataToRedux = {};
    // process the parse socket msg
    MapEventToProcess[event_type as keyof typeof MapEventToProcess](dataToRedux, payload);
    // this is sent as a reply ONLY AFTER the first time
    bufferQueue.push(dataToRedux);

    if (bufferQueue.length > 0  && (bufferQueue.length >= 1000 || bufferWindow === 0)) {
        // sending Data to the Main thread to store it in Redux
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
