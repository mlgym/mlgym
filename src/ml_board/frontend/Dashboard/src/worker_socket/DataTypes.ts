import { Row } from "../redux/table/tableSlice";
// import { evalResultCustomData } from "./event_handlers/evaluationResultDataHandler";
import { ChartUpdate } from "./event_handlers/EvaluationResultHandler";


// ========================= data types ============================//

export interface DataFromSocket {
    event_type: string,
    creation_ts: number,
    payload: JSON //NOTE: JSON (instead of EvaluationResultPayload and so) because some types have a key renamed :(
}

export interface DataToRedux {
    tableData?: Row,
    // evaluationResultsData?: evalResultCustomData,
    chartsUpdates?: ChartUpdate[],
    status?: any,
}