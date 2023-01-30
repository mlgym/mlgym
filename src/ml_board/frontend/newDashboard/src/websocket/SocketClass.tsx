import socketIO from 'socket.io-client';

const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

type SocketClassInterface = {
    defaultURL: string,
    dataCallback: Function | null
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
            socket.emit('join', { rooms: [runId], client_id: "3000" });
        });

        socket.on('mlgym_event', (msg) => {
            let parsedMsg = JSON.parse(msg);
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