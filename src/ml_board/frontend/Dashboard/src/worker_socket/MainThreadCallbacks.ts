import { DataFromSocket, DataToRedux } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData from "./event_handlers/EvaluationResultHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// ========================= variables ============================//

// Hashing is faster instead of switching over the the eventType
const MapEventToProcess: { [event: string]: (output: DataToRedux, input: JSON) => void } = {
    [MLGYM_EVENT.JOB_STATUS]: (dataToRedux: DataToRedux, data: JSON): void => { dataToRedux.tableData.push(handleJobStatusData(data)) },
    [MLGYM_EVENT.JOB_SCHEDULED]: (dataToRedux: DataToRedux, data: JSON): void => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (dataToRedux: DataToRedux, data: JSON): void => {
        const { experiment_id, charts_updates, table_scores } = handleEvaluationResultData(data);
        dataToRedux.chartsUpdates.push(...charts_updates);
        dataToRedux.tableData.push({ experiment_id, ...table_scores });
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: (dataToRedux: DataToRedux, data: JSON): void => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (dataToRedux: DataToRedux, data: JSON): void => { dataToRedux.tableData.push(handleExperimentStatusData(data)) },
};


// ========================= Callbacks to update the MainThread ============================//
export const updateMainThreadCallback = (bufferedSocketData: Array<JSON>) => {
    // create a placeholder with empty buffers to send to redux
    const bufferedDataToRedux: DataToRedux = {
        tableData: [],
        chartsUpdates: []
    };
    // loop over all incoming data from socket
    for (const data of bufferedSocketData) {
        // parse data from socket then extract event_type and payload
        const { data: { event_type, payload } } = data as DataFromSocket;
        // process the payload and load it into the DataToRedux object
        MapEventToProcess[event_type as keyof typeof MapEventToProcess](bufferedDataToRedux, payload);
    }
    // sending Data to the Main thread to store it in Redux
    postMessage(bufferedDataToRedux);
};

// NOTE: no need to buffer these callbacks as we want them to be in real time!!!
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
