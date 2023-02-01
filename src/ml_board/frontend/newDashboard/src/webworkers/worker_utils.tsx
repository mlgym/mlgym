import SocketClass from '../websocket/SocketClass';
import { handleEvaluationResultData, evalResultCustomData, evalResultSocketData } from './event_handlers/evaluationResultDataHandler';
import EVENT_TYPE from './socketEventConstants';

let webSocket = null;

type parsedSocketData = {
    creation_ts: BigInteger,
    event_type: string,
    payload: evalResultSocketData //as you handle experiment_status, job_status, keep adding: evalResultSocketData | expStatusSocketData | jobStatusSocketData like this & so on...
}

const workerOnMessageCallback = (evalResultCustomData:evalResultCustomData, parsedSocketData:parsedSocketData)=>{

    let eventType = parsedSocketData["event_type"].toLowerCase();
    let dataToUpdateReduxInChart = null;
    let dataToUpdateReduxInDashboard = null
    
    switch(eventType) {
        case EVENT_TYPE.JOB_STATUS:
            console.log("Job Status found")
            break;
        case EVENT_TYPE.JOB_SCHEDULED:
            console.log("Job scheduled found")
            break;
        case EVENT_TYPE.EVALUATION_RESULT:
            dataToUpdateReduxInChart = handleEvaluationResultData(EVENT_TYPE.EVALUATION_RESULT, evalResultCustomData, parsedSocketData["payload"]);
            // TODO: make handleExperimentStatusDataForDashboard()
            dataToUpdateReduxInDashboard = "handleExperimentStatusDataForDashboard()"
            break;
        case EVENT_TYPE.EXPERIMENT_CONFIG:
            console.log("Exp config found")
            break;
        case EVENT_TYPE.EXPERIMENT_STATUS:
            console.log("Exp status found")
            break;
        default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT);
    }
    postMessage({dataToUpdateReduxInChart, dataToUpdateReduxInDashboard});
}

onmessage = (e) => {
    const reduxData = e.data
    let result = null;
    try {
        webSocket = new SocketClass(Object((parsedSocketData:parsedSocketData)=>workerOnMessageCallback(reduxData,parsedSocketData)));
        webSocket.init();
        result = EVENT_TYPE.SOCKET_CONN_SUCCESS;
    }
    catch(e) {
        result = EVENT_TYPE.SOCKET_CONN_FAIL;
    }
    postMessage(result);
}