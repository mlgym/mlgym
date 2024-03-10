import { connectionMainThreadCallback, msgCounterIncMainThreadCallback, pingMainThreadCallback, throughputMainThreadCallback, updateMainThreadCallback } from './MainThreadCallbacks';

// ========================= variables ============================//
// Ping to measure Round Trip Time (RTT)
let pinging_interval: NodeJS.Timer; // for idealy pinging the server
const period: number = 1; // specifying how long the pinging_interval in seconds
let lastPing: number = -1;
let lastPong: number = -1; // the actual ping is calculated = lastPong - lastPing
// A counter to measure the throughput
let msgCountPerPeriod: number = 0;
// Buffering Window
const BUFFER_WINDOW_LIMIT_IN_MESSAGES = 256;
const bufferQueue: Array<JSON> = []; //NOTE: no fear of a race conditions as JS runs on a single thread!

// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebSocket~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
const initSimulation = (filePath: string) => {
    console.log(process.env.PUBLIC_URL + filePath);
    fetch(process.env.PUBLIC_URL + filePath)
        .then(res => res.text())
        .then(text => {
            const lineGenerator = (function* () {
                for (const line of text.split('\n')) {
                    yield line;
                }
            })();

            onConnect();

            (function logNextLine() {
                const { value, done } = lineGenerator.next();
                if (done) {
                    stop();
                } else {
                    setTimeout(logNextLine, 100 * Math.random());
                    process_mlgym_event(JSON.parse(value));
                }
            })();
        })
        .catch(error => console.error(error));
};

// ========================= connection events ============================//
const onConnect = () => {
    pinging_interval = setInterval(send_ping_to_websocket_server, period * 1000);
    connectionMainThreadCallback(true);
};

// ========================= data driven events ============================//
const process_mlgym_event = (msg: JSON) => {
    bufferQueue.push(msg);
    if (bufferQueue.length >= BUFFER_WINDOW_LIMIT_IN_MESSAGES) {
        flushBufferingWindow();
    }
    msgCountPerPeriod++;
    msgCounterIncMainThreadCallback();
};

const onPongReceivedfromWebsocketServer = () => {
    lastPong = new Date().getTime();
    pingMainThreadCallback(lastPong - lastPing);
};

// ========================= helper methods ============================//
const send_ping_to_websocket_server = () => {
    lastPing = new Date().getTime();
    throughputMainThreadCallback(msgCountPerPeriod / period);
    msgCountPerPeriod = 0;
    setTimeout(onPongReceivedfromWebsocketServer, 1000 * Math.random());
};

const stop = () => {
    clearInterval(pinging_interval);
    throughputMainThreadCallback(0);
    pingMainThreadCallback(0);
};

const flushBufferingWindow = () => {
    console.log(bufferQueue.length)
    updateMainThreadCallback(bufferQueue);
    bufferQueue.length = 0;
};

// =~=~=~=~=~=~=~=~=~=~=~=~=~= ~WebWorker~ =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=//
onmessage = ({ data }: MessageEvent) => {
    console.log(`>>>>>>>> WebWorker with Dummy WebSocket ${data}`);
    
    // if (data === "CLOSE_SOCKET")
    //     stopSimulation();
    // else if (data.gridSearchId !== undefined && data.socketConnectionUrl !== undefined)
    initSimulation("/event_storage/2024-02-14--22-15-46/event_storage.log");
};
