import SocketClass from '../websocket/SocketClass';

onmessage = (e) => {
    const data = e.data
    if(validateEventData(data)) {
        doAction(data);
    } else {
        console.log('Invalid message data passed from main thread so taking no action');
    }
}

const validateEventData = (data: any) => {
    //Validate all the request from main thread if you want to follow strict communication protocols
    //between main thread and the worker thread
    // if (data === "START") {
        return true;
    // }
    // else {
    //     return false;
    // }
}

let webSocket = null;

const workerOnMessageCallback = (data: any) => {
    postMessage(data)
}

const doAction = (reduxData: any) => {
    let result = null;
    try {
        webSocket = new SocketClass(reduxData, Object(workerOnMessageCallback));
        webSocket.init();
        result = "SUCCESS";
    }
    catch(e) {
        result = "FAIL";
    }
    postMessage(result);
}