// =================== API TYPES ======================

import internal from "stream";

interface BaseMessageType {
    event_id: number;
}

interface EventInfoType {
    event_type: string;
    creation_ts: number;
}

export type JobStatusPayloadType = {
    job_id: number;
    job_type: string; //<CALC, TERMINATE>
    status: string; //<INIT, RUNNING, DONE>,
    experiment_id: string; // <path_to_model>
    starting_time: number;
    finishing_time: number;
    error?: string;
    stacktrace?: string;
    device?: string // "GPU {1, ..., n}" or "CPU"
}

export type JobStatusInnerType = {
    payload: JobStatusPayloadType
} & EventInfoType


export type JobStatusType = { data: JobStatusInnerType, } & BaseMessageType


export type JobStatusMessageCollectionType = {
    messages: Array<JobStatusType>;
    job_id_to_latest_message_index: {[id: number]: number;}
}


export type IOStatsType = {
    msgTS: Array<number>;
    lastPing: number;
    lastPong: number;
    isConnected: boolean;
};