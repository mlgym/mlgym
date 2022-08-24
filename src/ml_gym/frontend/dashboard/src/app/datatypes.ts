// =================== API TYPES ======================

interface BaseMessageType {
    event_id: number;
}

interface EventInfoType {
    event_type: string;
    creation_ts: number;
}


// Job status

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


// Model status

export type ModelStatusPayloadType = {
    experiment_id: string;
    status: string; // <TRAINING, EVALUATING>,,
    num_epochs: number; //<CALC, TERMINATE>
    current_epoch: number;
    splits: Array<string>;
    current_split: string;
    num_batches: number;
    current_batch: number
}


export type ModelStatusInnerType = {
    payload: ModelStatusPayloadType
} & EventInfoType

export type ModelStatusType = { data: ModelStatusInnerType, } & BaseMessageType

// EXPERIMENT CONFIG

export type ExperimentConfigPayloadType = {
    grid_search_id: string;
    experiment_id: string;
    job_id: number; 
    config: any; 
}

export type ExperimentConfigInnerType = {
    payload: ExperimentConfigPayloadType
} & EventInfoType

export type ExperimentConfigType = { data: ExperimentConfigInnerType, } & BaseMessageType

// MODEL EVALUATION
export type MetricScoreType = {
    metric: string;
    split: string;
    score: number
}

export type LossScoreType = {
    loss: string;
    split: string;
    score: number
}

export type ModelEvaluationPayloadType = {
    epoch: number;
    experiment_id: string; 
    metric_scores: Array<MetricScoreType>;
    loss_scores: Array<LossScoreType>;
}

export type ModelEvaluationInnerType = {
    payload: ModelEvaluationPayloadType
} & EventInfoType

export type ModelEvaluationType = { data: ModelEvaluationInnerType, } & BaseMessageType

// AG GRID TYPES

export type JobStatusRowType = {
    job_id: number;
    job_type: string; //<CALC, TERMINATE>
    job_status: string; //<INIT, RUNNING, DONE>,
    experiment_id: string; // <path_to_model>
    starting_time: number;
    finishing_time: number;
    error?: string;
    stacktrace?: string;
    device?: string // "GPU {1, ..., n}" or "CPU"
}

export type ModelStatusRowType = {
    experiment_id: string;
    model_status: string; // <TRAINING, EVALUATING>,,
    num_epochs: number; //<CALC, TERMINATE>
    current_epoch: number;
    splits: Array<string>;
    current_split: string;
    epoch_progress: number;
    batch_progress: number
}



// REDUX STORE

export type JobStatusMessageCollectionType = {
    messages: Array<JobStatusType>;
    job_id_to_latest_message_index: { [id: number]: number; }
}

export type ModelStatusMessageCollectionType = {
    messages: Array<ModelStatusType>;
    experiment_id_to_latest_message_index: { [id: string]: number; }
}

export type ExperimentConfigMessageCollectionType = {
    messages: Array<ModelStatusType>;
    experiment_id_to_message_index: { [id: string]: number; }
}

export type ModelEvaluationMessageCollectionType = {
    messages: Array<ModelEvaluationType>;
};


export type IOStatsType = {
    msgTS: Array<number>;
    lastPing: number;
    lastPong: number;
    isConnected: boolean;
};

export type FilterConfigType = {
    metricFilterRegex: string;
    tmpMetricFilterRegex: string;
};
