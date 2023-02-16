import { Experiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { Job } from '../redux/jobs/jobSlice';
import SocketClass, { DataFromSocket, PingPong } from '../websocket/SocketClass';
import handleEvaluationResultData, { evalResultCustomData, EvaluationResultPayload } from './event_handlers/evaluationResultDataHandler';
import handleExperimentStatusData from './event_handlers/ExperimentStatusHandler';
import handleJobStatusData from './event_handlers/JobStatusHandler';
import { EVENT_TYPE, SOCKET_STATUS } from './socketEventConstants';

export interface DataToRedux {
    jobStatusData?: Job,
    experimentStatusData?: Experiment,
    evaluationResultsData?: evalResultCustomData,
    latest_split_metric?: EvaluationResultPayload,
    status?: any,
}

const workerOnMessageCallback = (evalResultCustomData: evalResultCustomData, parsedSocketData: DataFromSocket) => {

    const eventType = parsedSocketData.event_type.toLowerCase();
    const dataToRedux: DataToRedux = {};
    switch (eventType) {
        case EVENT_TYPE.JOB_STATUS:
            dataToRedux.jobStatusData = handleJobStatusData(parsedSocketData.payload);
            break;
        case EVENT_TYPE.JOB_SCHEDULED:
            console.log("Job scheduled found")
            break;
        case EVENT_TYPE.EVALUATION_RESULT:
            // TODO: get the "latest_split_metric" in the experimentsSlice too
            // just save the value directly in the Experiment, since the table is being formed from there
            // later decide if the column names are going to stay hard coded or inducted from the incoming messages 
            const evalResPayload = parsedSocketData.payload as unknown as EvaluationResultPayload;
            dataToRedux.evaluationResultsData = handleEvaluationResultData(evalResultCustomData, evalResPayload);
            dataToRedux.latest_split_metric = evalResPayload;
            break;
        case EVENT_TYPE.EXPERIMENT_CONFIG:
            console.log("Exp config found")
            break;
        case EVENT_TYPE.EXPERIMENT_STATUS:
            dataToRedux.experimentStatusData = handleExperimentStatusData(parsedSocketData.payload);
            break;
        default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT);
    }
    // this is sent as a reply ONLY AFTER the first time
    postMessage(dataToRedux);
}

const ping_pong_callback = (type: PingPong, time: number) => {
    postMessage({ status: { type, time } } as DataToRedux);
};

onmessage = (e) => {
    const reduxData = e.data
    let result = null;
    try {
        const webSocket = new SocketClass(
            (parsedSocketData: DataFromSocket) => workerOnMessageCallback(reduxData, parsedSocketData),
            (type: PingPong, time: number) => ping_pong_callback(type, time)
        );
        webSocket.init();
        result = SOCKET_STATUS.SOCKET_CONN_SUCCESS;
    }
    catch (e) {
        result = SOCKET_STATUS.SOCKET_CONN_FAIL;
    }
    // this is sent as a reply ONLY IN the first time
    postMessage(result);
}