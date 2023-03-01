import socketIO, { Socket } from 'socket.io-client';
import { DataFromSocket } from './DataTypes';
import { connectionMTCb, msgCounterIncMTCb, pingMTCb, throughputMTCb, updateMTCb } from './MainThreadCallbacks';


// ========================= variables ============================//

const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

let interval: NodeJS.Timer;
let lastPing: number = -1;
let lastPong: number = -1;
const period: number = 10;
let msgCountPerPeriod: number = 0;


// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebSocket~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
const socket: Socket = socketIO(DEFAULT_URL, { autoConnect: true });
console.log("WebSocket initialized");


// ========================= connection events ============================//
socket.on('connect', () => {
    // TODO:ASK how exactly should the join happen? and this was in the old code const runId = "mlgym_event_subscribers";
    // Max added bug report here: https://github.com/mlgym/mlgym/issues/134
    socket.emit('join', { rooms: ["mlgym_event_subscribers"] });
    // start periodic server pining
    interval = setInterval(pinging, period * 1000, socket);
    // flag main thread that connection is on
    connectionMTCb(true);
});

socket.on('disconnect', (reason: Socket.DisconnectReason) => stop(reason));

socket.on('connect_error', (err: Error) => stop(err));


// ========================= data driven events ============================//
socket.on('mlgym_event', (msg) => {
    const parsedMsg: DataFromSocket = JSON.parse(msg);
    // update the redux state on the main thread
    updateMTCb(parsedMsg);
    // message count for calculating the throughput
    msgCountPerPeriod++;
    // flag main thread to increment the number of incoming messages
    msgCounterIncMTCb();
});

socket.on('pong', () => {
    // on Pong , save time of receiving 
    lastPong = new Date().getTime();
    // calculate the ping and send it to the MainThread
    pingMTCb(lastPong - lastPing);
});

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
}

const stop = (why: Error|Socket.DisconnectReason) => {
    console.log(`${why instanceof Error ? "connection" /* error */: "disconnected"} : ${why}`);
    // halt periodic server pining
    clearInterval(interval);
    // flag main thread that connection is off
    connectionMTCb(false);
    // force throughput back to 0, as it won't update when the interval is cleared
    throughputMTCb(0);
    // force ping back to 0, it doesn't make sense to update it accurately if the connection is down anyways
    pingMTCb(0);
}


// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebWorker~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
// TODO: Remove this after handling the current situation with evaluation_result
// TODO: OR MAYBE! it is useful for sending the URL to the socket ????
onmessage = ({ data }: MessageEvent) => {
    if(data === "CLOSE_SOCKET")
        socket.close();
    console.log(data);
};
