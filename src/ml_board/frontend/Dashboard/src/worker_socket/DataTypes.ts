import { Row } from "../redux/table/tableSlice";
import { ChartUpdate } from "./event_handlers/EvaluationResultHandler";


// ========================= data types ============================//

// raw data coming in directly from the websocket server
export interface DataFromSocket extends JSON {
    event_id: string,
    data: {
        event_type: string,
        creation_ts: number,
        payload: JSON //NOTE: JSON (instead of EvaluationResultPayload and so) because some types have a key renamed :(
    }
}

export interface BufferedDataFromSocket extends JSON {
    event_id: string,
    data: Array<DataFromSocket>
}

export interface DataToRedux {
    tableHeaders?: string[],
    tableData: Row[],
    chartsUpdates: ChartUpdate[],
    status?: any,
}