import { io } from 'socket.io-client';
import EVENT_TYPE from './socketEventConstants';
import handleEvaluationResultData from './event_handlers/evaluationResultDataHandler';

const DEFAULT_URL = 'http://127.0.0.1:7000/';

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

    constructor(reduxData = undefined, dataCallback = null, socketURL = null) {
        this.reduxData = reduxData
        this.defaultURL = socketURL || DEFAULT_URL
        this.dataCallback = dataCallback
    }

    init = () => {
        let socket = io(this.defaultURL, { autoConnect: true });
        let runId = "mlgym_event_subscribers";
        
        socket.open();
        
        socket.emit('ping', () => {
            // console.log("ping");
        });
        
        socket.on('connect', () => {
            socket.emit('join', { rooms: [runId], client_id: "3000" });
        });

        socket.on('mlgym_event', (msg) => {
            try {
                let parsedMsg = JSON.parse(msg);
                this.handleEventMessage(parsedMsg);
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

        socket.on('pong', () => {
            // console.log("pong");
        });
    }

    handleEventMessage = (parsedMsg: parsedMsg) => {
        let eventType = parsedMsg["event_type"].toLowerCase();
        let result = null;

        switch(eventType) {
            case EVENT_TYPE.JOB_STATUS:
                console.log("Job Status found")
                break;
            case EVENT_TYPE.JOB_SCHEDULED:
                console.log("Job scheduled found")
                break;
            case EVENT_TYPE.EVALUATION_RESULT:
                if(this.reduxData !== undefined) {
                    result = handleEvaluationResultData(parsedMsg["payload"], this.reduxData);                    
                }
                break;
            case EVENT_TYPE.EXPERIMENT_CONFIG:
                console.log("Exp config found")
                break;
            case EVENT_TYPE.EXPERIMENT_STATUS:
                console.log("Exp status found")
                break;
            default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT);
        }
        // console.log(result);
        if (this.dataCallback) {
            this.dataCallback(result);
        }
    }
}

export default SocketClass;