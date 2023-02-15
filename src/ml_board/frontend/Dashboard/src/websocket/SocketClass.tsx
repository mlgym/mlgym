import socketIO, { Socket } from 'socket.io-client';

const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

export type PingPong = "PING" | "PONG"

interface SocketClassInterface {
    socketURL: string,
    interval: NodeJS.Timer;
    lastPing: number;
    lastPong: number;
}

export interface DataFromSocket {
    event_type: string,
    creation_ts: number,
    payload: JSON // | EvaluationResultPayload // JSON because the some types have a key renamed :(
}

class SocketClass implements SocketClassInterface {

    // definite assignment assertion [https://stackoverflow.com/questions/67351411/what-s-the-difference-between-definite-assignment-assertion-and-ambient-declarat]
    interval!: NodeJS.Timer;
    lastPing: number = -1;
    lastPong: number = -1;

    constructor(
        public dataCallback: (data: DataFromSocket) => void,
        public ping_pong: (type: PingPong, time: number) => void,
        public socketURL: string = '',
    ) {
        this.socketURL = socketURL || DEFAULT_URL
        this.dataCallback = dataCallback
        this.ping_pong = ping_pong
    }

    init = () => {

        let socket = socketIO(this.socketURL, { autoConnect: true });
        let runId = "mlgym_event_subscribers";

        socket.open();

        socket.on('connect', () => {
            socket.emit('join', { rooms: [runId] });
            this.interval = setInterval(this.pinging, 10000, socket);
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
            clearInterval(this.interval);
        });

        socket.on('pong', () => {
            this.lastPong = new Date().getTime();
            this.ping_pong('PONG', this.lastPong);
        });
    }

    pinging = (socket: Socket) => {
        if (this.lastPong > this.lastPing || this.lastPing === -1) {
            this.lastPing = new Date().getTime();
            socket.emit('ping');
            this.ping_pong('PING', this.lastPing);
        }
    }
}

export default SocketClass;