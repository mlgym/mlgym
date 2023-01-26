import SocketClass from '../websocket/SocketClass';
import { handleExperimentStatusData, reduxData, dataFromSocket } from './event_handlers/evaluationResultDataHandler';

let webSocket = null;

const workerOnMessageCallback = (reduxData: reduxData, dataFromSocket: dataFromSocket) => {
    let dataToUpdateRedux = handleExperimentStatusData(reduxData, dataFromSocket);
    postMessage(dataToUpdateRedux);
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