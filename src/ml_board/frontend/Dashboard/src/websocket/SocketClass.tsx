import socketIO, { Socket } from 'socket.io-client';
import { settingConfigsInterface } from "../app/App";

// const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

// export type PingPong = "PING" | "PONG"

interface SocketClassInterface {
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
    readonly period: number = 10;
    msgCountPerPeriod: number = 0;

    constructor(
        private dataCallback: (data: DataFromSocket) => void,
        private connectionCb: (isConnected: boolean) => void,
        private pingCb: (time: number) => void,
        private msgCountIncCb: () => void,
        private throughputCb: (throughput: number) => void
    ) {
        this.dataCallback = dataCallback;
        this.connectionCb = connectionCb;
        this.pingCb = pingCb;
        this.msgCountIncCb = msgCountIncCb;
    }

    init = (settingConfigs: settingConfigsInterface) => {
        // settingConfigs - are the configurations sent by user for making socket connection request
        const socket = socketIO(settingConfigs.socketConnectionUrl, { autoConnect: true });
        const runId = settingConfigs.gridSearchId;

        socket.open();

        socket.on('connect', () => {
            socket.emit('join', { rooms: [runId] });
            this.interval = setInterval(this.pinging, this.period * 1000, socket);
            this.connectionCb(true);
        });

        socket.on('mlgym_event', (msg) => {
            const parsedMsg: DataFromSocket = JSON.parse(msg);
            this.msgCountPerPeriod++;
            this.msgCountIncCb();
            if (this.dataCallback) {
                this.dataCallback(parsedMsg);
            }
        });

        socket.on('connect_error', (err: Error) => this.stop(err));

        socket.on('disconnect', (reason: Socket.DisconnectReason) => this.stop(reason));

        socket.on('pong', () => {
            // on Pong , save time of receiving 
            this.lastPong = new Date().getTime();
            // calculate the ping and send it to the MainThread
            this.pingCb(this.lastPong - this.lastPing);
        });
    }

    pinging = (socket: Socket) => {
        // if Pong was received after sending a Ping 
        // if no Ping was sent before
        if (this.lastPong > this.lastPing || this.lastPing === -1) {
            // save ping time
            this.lastPing = new Date().getTime();
            // ping the server
            socket.emit('ping');
        }

        // regardless of the if statement, this function runs every "period"
        this.throughputCb(this.msgCountPerPeriod / this.period)
        this.msgCountPerPeriod = 0;
    }

    stop = (why: any) => {
        console.log(`${why instanceof Error ? "connection" /* error */: "disconnected"} : ${why}`);
        clearInterval(this.interval);
        this.connectionCb(false);
        this.throughputCb(0);
        this.pingCb(0);
    }
}

export default SocketClass;