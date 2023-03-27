// import { Experiment } from "../redux/experiments/yetAnotherExperimentSlice";
// import { Job } from "../redux/jobs/jobSlice";
import { Row } from "../redux/table/tableSlice";
import { evalResultCustomData, EvaluationResultPayload } from "./event_handlers/evaluationResultDataHandler";


// ========================= data types ============================//

export interface DataFromSocket {
    event_type: string,
    creation_ts: number,
    payload: JSON // | EvaluationResultPayload // JSON because the some types have a key renamed :(
}

export interface DataToRedux {
    // jobStatusData?: Job,
    // experimentStatusData?: Experiment,
    tableData?: Row,
    evaluationResultsData?: evalResultCustomData,
    latest_split_metric?: EvaluationResultPayload,
    status?: any,
}