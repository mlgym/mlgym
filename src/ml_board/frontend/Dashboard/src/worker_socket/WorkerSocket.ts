import socketIO, { Socket } from 'socket.io-client';
import { settingConfigsInterface } from '../app/App';
import { connectionMainThreadCallback, msgCounterIncMainThreadCallback, pingMainThreadCallback, throughputMainThreadCallback, updateMainThreadCallback } from './MainThreadCallbacks';

// ========================= variables ============================//
let socket: Socket; // 'let' to initialize on funciton call
// Ping to measure Round Trip Time (RTT)
let pinging_interval: NodeJS.Timer; // for idealy pinging the server
const period: number = 1; // specifying how long the pinging_interval in seconds
let lastPing: number = -1;
let lastPong: number = -1; // the actual ping is calculated = lastPong - lastPing
// A counter to measure the throughput
let msgCountPerPeriod: number = 0;
// Buffering Window
const BUFFER_WINDOW_LIMIT_IN_SECONDS = 1;
const BUFFER_WINDOW_LIMIT_IN_MESSAGES = 1000;
const bufferQueue: Array<JSON> = []; //NOTE: no fear of a race conditions as JS runs on a single thread!
let buffering_interval: NodeJS.Timer;

// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebSocket~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
const initSocket = (settingConfigs: settingConfigsInterface) => {
    console.log("WebSocket initializing...");
    socket = socketIO(settingConfigs.socketConnectionUrl, { autoConnect: true });
    socket.on('connect', () => onConnect(socket, settingConfigs.gridSearchId, settingConfigs.restApiUrl));
    socket.on('disconnect', onDisconnect);
    socket.on('connect_error', onError);
    socket.on('mlgym_event', process_mlgym_event);
    socket.on('pong', onPongReceivedfromWebsocketServer);
};


// ========================= connection events ============================//
const onConnect = (socket: Socket, gridSearchId: string, restApiUrl: string) => {
    //NOTE: for testing with the dummy_server.py set runId = "mlgym_event_subscribers";
    // Max added bug report here: https://github.com/mlgym/mlgym/issues/134
    socket.emit('join', { rooms: [gridSearchId] });
    // start periodic server pining
    pinging_interval = setInterval(send_ping_to_websocket_server, period * 1000, socket);
    // flag main thread that connection is on
    connectionMainThreadCallback(true, gridSearchId, restApiUrl);
    // start periodic buffer flushing
    buffering_interval = setInterval(() => { bufferQueue.length > 0 && flushBufferingWindow() }, BUFFER_WINDOW_LIMIT_IN_SECONDS * 1000);
};

const onDisconnect = (reason: Socket.DisconnectReason) => stop(reason);

const onError = (err: Error) => stop(err);

// ========================= data driven events ============================//
const process_mlgym_event = (msg: JSON) => {
    // TODO: maybe here instead of just pushing, insert based on the "event_id" or "creation_ts"
    // push in the buffer
    bufferQueue.push(msg);
    // flush if bufferQueue is full
    if (bufferQueue.length >= BUFFER_WINDOW_LIMIT_IN_MESSAGES) {
        flushBufferingWindow();
    }
    // message count for calculating the throughput
    msgCountPerPeriod++;
    // flag main thread to increment the number of incoming messages
    msgCounterIncMainThreadCallback();
};

// ASK MAX: renaming to onPong or onPongReceived
const onPongReceivedfromWebsocketServer = () => {
    // on Pong , save time of receiving 
    lastPong = new Date().getTime();
    // calculate the ping and send it to the MainThread
    pingMainThreadCallback(lastPong - lastPing);
};

// ========================= helper methods ============================//

// ASK MAX: sendPingToServer or sendPing or pingToServer or pingingServer or pinging
const send_ping_to_websocket_server = (socket: Socket) => {
    // if Pong was received after sending a Ping 
    // if no Ping was sent before
    if (lastPong > lastPing || lastPing === -1) {
        // save ping time
        lastPing = new Date().getTime();
        // ping the server
        socket.emit('ping');
    }
    // calculate throughput and send it to the main thread
    throughputMainThreadCallback(msgCountPerPeriod / period);
    // reset message count to calculate throughput
    msgCountPerPeriod = 0;
};

const stop = (why: Error | Socket.DisconnectReason) => {
    console.log(`${why instanceof Error ? "connection" /* error */ : "disconnected"} : ${why}`);
    // halt periodic server pining
    clearInterval(pinging_interval);
    // halt periodic buffering
    clearInterval(buffering_interval);
    // flush just in case something is still in the buffer
    bufferQueue.length > 0 && flushBufferingWindow();
    // flag main thread that connection is off
    connectionMainThreadCallback(false);
    // force throughput back to 0, as it won't update when the interval is cleared
    throughputMainThreadCallback(0);
    // force ping back to 0, it doesn't make sense to update it accurately if the connection is down anyways
    pingMainThreadCallback(0);
};

// flush regardless whether the bufferQueue is full or not
const flushBufferingWindow = () => {
    // update the redux state on the main thread
    updateMainThreadCallback(bufferQueue);
    // clear the buffer
    bufferQueue.length = 0;
};

// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebWorker~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
// in the beginning and at the end
onmessage = ({ data }: MessageEvent) => {
    // for closing the socket!
    if (data === "CLOSE_SOCKET")
        socket.close();
    // sending the URL to the socket and other initialization parameters!
    else if (data.gridSearchId !== undefined && data.socketConnectionUrl !== undefined)
        // data is settingConfigs
        initSocket(data);
    // Debugging purposes 
    else
        console.log(data);
};
