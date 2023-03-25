import { Row } from "../redux/table/tableSlice";
import { evalResultCustomData } from "./event_handlers/evaluationResultDataHandler";


// ========================= data types ============================//

export interface DataFromSocket {
    event_type: string,
    creation_ts: number,
    payload: JSON // | EvaluationResultPayload // JSON because the some types have a key renamed :(
}

export interface DataToRedux {
    tableData?: Row,
    evaluationResultsData?: evalResultCustomData,
    status?: any,
}