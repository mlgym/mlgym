import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData, { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// Note: I don't like having anything here other than the callbacks but it is what it is :')
// ========================= variables ============================//
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
        // TODO: if handleEvaluationResultData is gonna get improved, then move the following inside of it
        // save the latest score values
        const { experiment_id, metric_scores, loss_scores } = evalResPayload;
        const scores: { [latest_split_metric_key: string]: number } = {};
        for (const metric of metric_scores) {
            scores[metric.split + "_" + metric.metric] = metric.score;
        }
        for (const loss of loss_scores) {
            scores[loss.split + "_" + loss.loss] = loss.score;
        }
        dataToRedux.tableData = { experiment_id, ...scores }
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: () => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: any) => { dataToRedux.tableData = handleExperimentStatusData(data) },
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
// ========================= helper methods ============================//
