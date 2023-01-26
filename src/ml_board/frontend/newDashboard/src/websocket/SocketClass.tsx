import socketIO from 'socket.io-client';

const DEFAULT_URL = 'http://localhost:7000/'; // or http://127.0.0.1:7000/'

type parsedMsg = {
    event_type: string,
    payload: any,
    event_id: number
}

type SocketClassInterface = {
    reduxData: {
        grid_search_id: string,
        experiments: {
            [key: string]: {
                data: {
                    labels: Array<number>,
                    datasets: Array<{
                        exp_id: number,
                        label: string,
                        data: Array<number>,
                        fill: Boolean,
                        backgroundColor: string,
                        borderColor: string 
                    }>
                },
                options: {
                    plugins: {
                        title: {
                            display: Boolean,
                            text: string,
                            color: string,
                            font: {
                                weight: string,
                                size: string
                            }
                        }
                    }
                },
                ids_to_track_and_find_exp_id: Array<number>
            };
        },
        colors_mapped_to_exp_id: {
            [key: number]: string
        }
    } | undefined,
    defaultURL: string,
    dataCallback: Function | null
}
class SocketClass implements SocketClassInterface {
    
    reduxData: {
        grid_search_id: string,
        experiments: {
            [key: string]: {
                data: {
                    labels: Array<number>,
                    datasets: Array<{
                        exp_id: number,
                        label: string,
                        data: Array<number>,
                        fill: Boolean,
                        backgroundColor: string,
                        borderColor: string 
                    }>
                },
                options: {
                    plugins: {
                        title: {
                            display: Boolean,
                            text: string,
                            color: string,
                            font: {
                                weight: string,
                                size: string
                            }
                        }
                    }
                },
                ids_to_track_and_find_exp_id: Array<number>
            };
        },
        colors_mapped_to_exp_id: {
            [key: number]: string
        }
    } | undefined
    defaultURL: string
    dataCallback: Function | null

    constructor(dataCallback = null, socketURL = null) {
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
            try {
                let parsedMsg = JSON.parse(msg);
                if (this.dataCallback) {
                    this.dataCallback(parsedMsg);
                }
            } 
            catch(error) {
                console.log("Websocket Event Error = ",error.message);
            }            
        });

        socket.on('connect_error', (err) => {
            console.log("connection error", err);
        })

        socket.on('disconnect', () => {
            console.log("disconnected");
        });

    }

    // handleEventMessage = (parsedMsg: parsedMsg) => {
    //     // let eventType = parsedMsg["event_type"].toLowerCase();
    //     // let result = null;

    //     // switch(eventType) {
    //     //     case EVENT_TYPE.JOB_STATUS:
    //     //         console.log("Job Status found")
    //     //         break;
    //     //     case EVENT_TYPE.JOB_SCHEDULED:
    //     //         console.log("Job scheduled found")
    //     //         break;
    //     //     case EVENT_TYPE.EVALUATION_RESULT:
    //     //         result = parsedMsg["payload"]
    //     //         break;
    //     //     case EVENT_TYPE.EXPERIMENT_CONFIG:
    //     //         console.log("Exp config found")
    //     //         break;
    //     //     case EVENT_TYPE.EXPERIMENT_STATUS:
    //     //         console.log("Exp status found")
    //     //         break;
    //     //     default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT);
    //     // }
    //     // console.log(result);
    //     if (this.dataCallback) {
    //         this.dataCallback(parsedMsg);
    //     }
    // }
}

export default SocketClass;