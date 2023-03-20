import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData from "./event_handlers/EvaluationResultHandler";
// import handleEvaluationResultData, { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// ========================= variables ============================//

// Hashing is faster instead of switching over the the eventType
const MapEventToProcess = {
    [MLGYM_EVENT.JOB_STATUS]: (dataToRedux: DataToRedux, data: JSON) => { dataToRedux.tableData = handleJobStatusData(data) },
    [MLGYM_EVENT.JOB_SCHEDULED]: () => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (dataToRedux: DataToRedux, data: JSON) => {
        const { experiment_id, charts_updates, table_scores } = handleEvaluationResultData(data);
        dataToRedux.chartsUpdates = charts_updates;
        dataToRedux.tableData = { experiment_id, ...table_scores };
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: () => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: JSON) => { dataToRedux.tableData = handleExperimentStatusData(data) },
};

// ========================= Callbacks to update the MainThread ============================//

export const updateMainThreadCallback = (parsedSocketData: DataFromSocket) => {
    const eventType = parsedSocketData.event_type.toLowerCase();
    const dataToRedux: DataToRedux = {};
    MapEventToProcess[eventType as keyof typeof MapEventToProcess](dataToRedux, parsedSocketData.payload);
    // this is sent as a reply ONLY AFTER the first time
    postMessage(dataToRedux);
};

export const pingMainThreadCallback = (ping: number) => {
    postMessage({ status: { ping } } as DataToRedux);
};

export const connectionMainThreadCallback = (isSocketConnected: boolean) => {
    postMessage({ status: { isSocketConnected } } as DataToRedux);
};

export const msgCounterIncMainThreadCallback = () => {
    postMessage({ status: "msg_count_increment" } as DataToRedux);
};

export const throughputMainThreadCallback = (throughput: number) => {
    postMessage({ status: { throughput } } as DataToRedux);
};