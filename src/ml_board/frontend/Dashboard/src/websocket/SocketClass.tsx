import socketIO from 'socket.io-client';

const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

interface SocketClassInterface {
    defaultURL: string,
    dataCallback: Function
}

export interface DataFromSocket {
    event_type: string,
    creation_ts: number,
    payload: JSON // | EvaluationResultPayload // JSON because the some types have a key renamed :(
}

class SocketClass implements SocketClassInterface {

    defaultURL: string
    dataCallback: Function

    constructor(dataCallback: Function, socketURL = null) {
        this.defaultURL = socketURL || DEFAULT_URL
        this.dataCallback = dataCallback
    }

    init = () => {

        let socket = socketIO(this.defaultURL, { autoConnect: true });
        let runId = "mlgym_event_subscribers";

        socket.open();

        socket.on('connect', () => {
            socket.emit('join', { rooms: [runId] });
        });

        socket.on('mlgym_event', (msg) => {
            const parsedMsg: DataFromSocket = JSON.parse(msg);
            if (this.dataCallback) {
                this.dataCallback(parsedMsg);
            }
        });

        socket.on('connect_error', (err) => {
            console.log("connection error", err);
        })

        socket.on('disconnect', () => {
            console.log("disconnected");
        });

    }
}

export default SocketClass;