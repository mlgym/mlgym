import { Experiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { Job } from '../redux/jobs/jobSlice';
import SocketClass from '../websocket/SocketClass';
import { dataFromSocket, handleEvaluationResultData, reduxData } from './event_handlers/evaluationResultDataHandler';
import handleExperimentStatusData from './event_handlers/ExperimentStatusHandler';
import handleJobStatusData from './event_handlers/JobStatusHandler';
import EVENT_TYPE from './socketEventConstants';

export interface DataToRedux {
    jobStatusData?: Job,
    experimentStatusData?: Experiment,
    evaluationResultsData?: reduxData,
}

const workerOnMessageCallback = (reduxData: reduxData, dataFromSocket: any) => {

    const eventType = dataFromSocket["event_type"].toLowerCase();
    const dataToRedux: DataToRedux = {};
    switch (eventType) {
        case EVENT_TYPE.JOB_STATUS:
            // TODO: HERE
            dataToRedux.jobStatusData = handleJobStatusData(dataFromSocket["payload"]);
            break;
        case EVENT_TYPE.JOB_SCHEDULED:
            console.log("Job scheduled found")
            break;
        case EVENT_TYPE.EVALUATION_RESULT:
            // TODO: make handleExperimentStatusDataForDashboard()
            dataToRedux.evaluationResultsData = handleEvaluationResultData(reduxData, dataFromSocket["payload"]);
            break;
        case EVENT_TYPE.EXPERIMENT_CONFIG:
            console.log("Exp config found")
            break;
        case EVENT_TYPE.EXPERIMENT_STATUS:
            // TODO: HERE
            dataToRedux.experimentStatusData = handleExperimentStatusData(dataFromSocket["payload"]);
            break;
        default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT);
    }
    // this is sent as a reply ONLY AFTER the first time
    postMessage(dataToRedux);
}

onmessage = (e) => {
    const reduxData = e.data
    let result = null;
    try {
        // ASK Vijul: how is this casting to "dataFromSocket" even possible? while sending the data to workerOnMessageCallback as "any"?
        const webSocket = new SocketClass(Object((dataFromSocket: dataFromSocket) => workerOnMessageCallback(reduxData, dataFromSocket)));
        webSocket.init();
        result = EVENT_TYPE.SOCKET_CONN_SUCCESS;
    }
    catch (e) {
        result = EVENT_TYPE.SOCKET_CONN_FAIL;
    }
    // this is sent as a reply ONLY IN the first time
    postMessage(result);
}