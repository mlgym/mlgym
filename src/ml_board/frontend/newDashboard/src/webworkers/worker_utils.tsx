import SocketClass from '../websocket/SocketClass';
import { handleExperimentStatusData, reduxData, dataFromSocket } from './event_handlers/evaluationResultDataHandler';
import EVENT_TYPE from './socketEventConstants';

let webSocket = null;

const workerOnMessageCallback = (reduxData: reduxData, dataFromSocket: any) => {

    let eventType = dataFromSocket["event_type"].toLowerCase();
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
            dataToUpdateReduxInChart = handleExperimentStatusData(EVENT_TYPE.EVALUATION_RESULT, reduxData, dataFromSocket["payload"]);
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
        webSocket = new SocketClass(Object((dataFromSocket:dataFromSocket)=>workerOnMessageCallback(reduxData,dataFromSocket)));
        webSocket.init();
        result = "SUCCESS";
    }
    catch(e) {
        result = "FAIL";
    }
    postMessage(result);
}