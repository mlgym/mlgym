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
    [MLGYM_EVENT.JOB_STATUS]: (dataToRedux: DataToRedux, data: any) => { dataToRedux.jobStatusData = handleJobStatusData(data) },
    [MLGYM_EVENT.JOB_SCHEDULED]: () => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (dataToRedux: DataToRedux, data: any) => {
        const evalResPayload = data as unknown as EvaluationResultPayload;
        dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, evalResPayload);
        dataToRedux.latest_split_metric = evalResPayload;
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: () => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: any) => { dataToRedux.experimentStatusData = handleExperimentStatusData(data) },
};

// ========================= Callbacks to update the MainThread ============================//

export const updateMainThreadCallback = (parsedSocketData: DataFromSocket) => {
    const eventType = parsedSocketData.event_type.toLowerCase();
    const dataToRedux: DataToRedux = {};
    // switch (eventType) {
    //     case MLGYM_EVENT.JOB_STATUS:
    //         dataToRedux.jobStatusData = handleJobStatusData(parsedSocketData.payload);
    //         break;
    //     case MLGYM_EVENT.JOB_SCHEDULED:
    //         console.log("Job scheduled found")
    //         break;
    //     case MLGYM_EVENT.EVALUATION_RESULT:
    //         // TODO: get the "latest_split_metric" in the experimentsSlice too
    //         // dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, parsedSocketData.payload as unknown as EvaluationResultPayload);
    //         // just save the value directly in the Experiment, since the table is being formed from there
    //         // later decide if the column names are going to stay hard coded or inducted from the incoming messages 
    //         const evalResPayload = parsedSocketData.payload as unknown as EvaluationResultPayload;
    //         dataToRedux.evaluationResultsData = handleEvaluationResultData(initialStateForGraphs, evalResPayload);
    //         dataToRedux.latest_split_metric = evalResPayload;
    //         break;
    //     case MLGYM_EVENT.EXPERIMENT_CONFIG:
    //         console.log("Exp config found")
    //         break;
    //     case MLGYM_EVENT.EXPERIMENT_STATUS:
    //         dataToRedux.experimentStatusData = handleExperimentStatusData(parsedSocketData.payload);
    //         break;
    //     default: throw new Error(MLGYM_EVENT.UNKNOWN_EVENT);
    // }
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
