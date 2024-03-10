import { Row } from "../redux/table/tableSlice";
import { BufferedDataFromSocket, DataFromSocket, DataToRedux, UpdatesObject } from "./DataTypes";
import { MLGYM_EVENT } from "./EventsTypes";
import handleEvaluationResultData from "./event_handlers/EvaluationResultHandler";
import handleExperimentStatusData from "./event_handlers/ExperimentStatusHandler";
import handleJobStatusData from "./event_handlers/JobStatusHandler";

// ========================= variables ============================//

const MapEventsFirstOccurrence: { [event: string]: boolean } = {};
// const TableHeaders: Set<string> = new Set();

// Hashing is faster instead of switching over the the eventType
const MapEventToProcess: { [event: string]: (input: JSON, output: UpdatesObject) => void } = {
    [MLGYM_EVENT.JOB_STATUS]: (data: JSON, update: UpdatesObject): void => {
        processForTable(handleJobStatusData(data), update, MLGYM_EVENT.JOB_STATUS);
    },
    [MLGYM_EVENT.JOB_SCHEDULED]: (data: JSON, update: UpdatesObject): void => console.log("Job scheduled found"),
    [MLGYM_EVENT.EVALUATION_RESULT]: (data: JSON, update: UpdatesObject): void => {
        const { experiment_id, charts_updates, table_scores } = handleEvaluationResultData(data);
        update.chartsUpdates.push(...charts_updates); // process for Charts
        processForTable({ experiment_id, ...table_scores }, update); // process for Table
    },
    [MLGYM_EVENT.EXPERIMENT_CONFIG]: (data: JSON, update: UpdatesObject): void => console.log("Exp config found"),
    [MLGYM_EVENT.EXPERIMENT_STATUS]: (data: JSON, update: UpdatesObject): void => {
        processForTable(handleExperimentStatusData(data), update, MLGYM_EVENT.EXPERIMENT_STATUS);
    },
};

// ========================= helper methods ============================//
// prepares the rows and the headers of the table
function processForTable(data: Row, update: UpdatesObject, key: string = ""): void {
    // if defined then merge otherwise take the data as the initial value
    Object.assign(update[data.experiment_id] ??= data, data);
    // check if the event_type is provided and if it was the first occurrence? if so return
    if (key && MapEventsFirstOccurrence[key]) return;
    // set the flag in order to not form the headers again
    MapEventsFirstOccurrence[key] = true;
    // else add every key in the row object to the headers
    Object.keys(update[data.experiment_id]).forEach(update.headers.add, update.headers);
}

// loops over buffers, whether created by the websocket or received as a buffered message
function processBuffer(bufferedSocketData: Array<JSON>, updatesHolder: UpdatesObject): void {
    // loop over all incoming data from socket
    for (const data of bufferedSocketData) {
        // assume incoming data type to be BufferedDataFromSocket and verify the event_id
        const data_from_socket = data as BufferedDataFromSocket;
        if (data_from_socket.event_id === "batched_events") {
            // if that's the case then do a recursive call on the data and skip afterwards
            processBuffer(data_from_socket.data, updatesHolder)
            continue;
            // NOTE: due to the nature of the incoming messages we know that there is 
            // never a BufferedDataFromSocket inside of another BufferedDataFromSocket
            // so it's safe to say that this recursion is 1-level-deep only!
        }
        // parse data from socket then extract event_type and payload
        const { event_type, payload } = data as any;
        // process the payload and load it into the UpdatesObject Object to be later processed into DataToRedux object
        MapEventToProcess[event_type as keyof typeof MapEventToProcess](payload, updatesHolder);
    }
}

// prepare the update to match the redux accepted format 
function processUpdatesIntoReduxData({ headers, chartsUpdates, ...experiments }: UpdatesObject): DataToRedux {
    // TODO: maybe compare the size of the set to its previous size instead of sending every time? 
    // NOTE: currently because of the different headers that are received everytime 
    // because of the MLGYM_EVENT.EVALUATION_RESULT, sending nearly all the time is inevitable 
    return {
        tableHeaders: headers.size > 0 ? [...headers] : undefined,
        tableData: Object.values(experiments),
        chartsUpdates: chartsUpdates,
    };
}

// ========================= Callbacks to update the MainThread ============================//
export const updateMainThreadCallback = (bufferedSocketData: Array<JSON>) => {
    // create a place holder for the incoming updates
    const updatesHolder: UpdatesObject = {
        headers: new Set(),
        chartsUpdates: []
    };
    // Process the buffer coming from the socket and populate updatesHolder object accordingly
    processBuffer(bufferedSocketData, updatesHolder);
    // sending Data to the Main thread to store it in Redux after processing it into the right format
    postMessage(processUpdatesIntoReduxData(updatesHolder));
};

// NOTE: no need to buffer these callbacks as we want them to be in real time!!!
export const pingMainThreadCallback = (ping: number) => {
    postMessage({ status: { ping } } as DataToRedux);
};

export const connectionMainThreadCallback = (isSocketConnected: boolean, gridSearchId?: string, restApiUrl?: string) => {
    postMessage({ status: { isSocketConnected, gridSearchId, restApiUrl } } as DataToRedux);
};

export const msgCounterIncMainThreadCallback = () => {
    postMessage({ status: "msg_count_increment" } as DataToRedux);
};

export const throughputMainThreadCallback = (throughput: number) => {
    postMessage({ status: { throughput } } as DataToRedux);
};
