import { Row } from "../redux/table/tableSlice";
import { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";


// ========================= data types ============================//

export interface DataFromSocket extends JSON {
    event_type: string,
    creation_ts: number,
    payload: JSON // | EvaluationResultPayload // JSON because the some types have a key renamed :(
}

export interface DataToRedux {
    tableData?: Row,
    evaluationResultsData?: evalResultCustomData,
    latest_split_metric?: EvaluationResultPayload,
    status?: any,
}