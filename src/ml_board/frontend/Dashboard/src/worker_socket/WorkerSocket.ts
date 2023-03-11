import socketIO, { Socket } from 'socket.io-client';
import { settingConfigsInterface } from '../app/App';
import { DataFromSocket } from './DataTypes';
import { connectionMTCb, msgCounterIncMTCb, pingMTCb, throughputMTCb, updateMTCb } from './MainThreadCallbacks';


// ========================= variables ============================//

// const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

let interval: NodeJS.Timer;
let lastPing: number = -1;
let lastPong: number = -1;
const period: number = 10;
let msgCountPerPeriod: number = 0;
let socket: Socket;


// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebSocket~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
const initSocket = (settingConfigs: settingConfigsInterface) => {
    socket = socketIO(settingConfigs.socketConnectionUrl, { autoConnect: true });
    console.log("WebSocket initialized");
    socket.on('connect', () => connect(socket, settingConfigs.gridSearchId));
    socket.on('disconnect', disconnect);
    socket.on('connect_error', connect_error);
    socket.on('mlgym_event', mlgym_event);
    socket.on('pong', pong);
};


// ========================= connection events ============================//
const connect = (socket: Socket, runId: string) => {
    // TODO:ASK how exactly should the join happen? and this was in the old code const runId = "mlgym_event_subscribers";
    // Max added bug report here: https://github.com/mlgym/mlgym/issues/134
    socket.emit('join', { rooms: [runId] });
    // start periodic server pining
    interval = setInterval(pinging, period * 1000, socket);
    // flag main thread that connection is on
    connectionMTCb(true);
};

const disconnect = (reason: Socket.DisconnectReason) => stop(reason);

const connect_error = (err: Error) => stop(err);


// ========================= data driven events ============================//
// const mlgym_event = (msg:JSON) => {
const mlgym_event = (msg: string) => {
    const parsedMsg: DataFromSocket = JSON.parse(msg);
    // update the redux state on the main thread
    updateMTCb(parsedMsg);
    // message count for calculating the throughput
    msgCountPerPeriod++;
    // flag main thread to increment the number of incoming messages
    msgCounterIncMTCb();
};

const pong = () => {
    // on Pong , save time of receiving 
    lastPong = new Date().getTime();
    // calculate the ping and send it to the MainThread
    pingMTCb(lastPong - lastPing);
};

// ========================= helper methods ============================//

const pinging = (socket: Socket) => {
    // if Pong was received after sending a Ping 
    // if no Ping was sent before
    if (lastPong > lastPing || lastPing === -1) {
        // save ping time
        lastPing = new Date().getTime();
        // ping the server
        socket.emit('ping');
    }
    // calculate throughput and send it to the main thread
    throughputMTCb(msgCountPerPeriod / period)
    // reset message count to calculate throughput
    msgCountPerPeriod = 0;
};

const stop = (why: Error | Socket.DisconnectReason) => {
    console.log(`${why instanceof Error ? "connection" /* error */ : "disconnected"} : ${why}`);
    // halt periodic server pining
    clearInterval(interval);
    // flag main thread that connection is off
    connectionMTCb(false);
    // force throughput back to 0, as it won't update when the interval is cleared
    throughputMTCb(0);
    // force ping back to 0, it doesn't make sense to update it accurately if the connection is down anyways
    pingMTCb(0);
};


// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebWorker~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
// TODO: Remove this after handling the current situation with evaluation_result
// TODO: OR MAYBE! it is useful for sending the URL to the socket ????
onmessage = ({ data }: MessageEvent) => {
    if (data === "CLOSE_SOCKET")
        socket.close();
    else if (data.gridSearchId !== undefined && data.socketConnectionUrl !== undefined) {
        // data is settingConfigs
        initSocket(data);
    }
    console.log(data);
};
