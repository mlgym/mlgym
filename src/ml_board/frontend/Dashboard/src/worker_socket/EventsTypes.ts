// as no more event types are going to be created, it's better to have all of them just here in one place instead of defined in their own files with their handlers

// the name of 'mlgym_event's received on the socket
export const MLGYM_EVENT = Object.freeze({
    JOB_STATUS: "job_status",
    JOB_SCHEDULED: "job_scheduled",
    EVALUATION_RESULT: "evaluation_result",
    EXPERIMENT_CONFIG: "experiment_config",
    EXPERIMENT_STATUS: "experiment_status",
    UNKNOWN_EVENT: "Unknown event type. No event handler for such event type.",
});