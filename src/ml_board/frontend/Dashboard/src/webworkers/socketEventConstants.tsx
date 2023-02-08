export const EVENT_TYPE = Object.freeze({
    JOB_STATUS: "job_status",
    JOB_SCHEDULED: "job_scheduled",
    EVALUATION_RESULT: "evaluation_result",
    EXPERIMENT_CONFIG: "experiment_config",
    EXPERIMENT_STATUS: "experiment_status",
    UNKNOWN_EVENT: "Unknown event type. No event handler for such event type.",
});

export const SOCKET_STATUS = Object.freeze({
    SOCKET_CONN_SUCCESS: "Socket Connection Successful",
    SOCKET_CONN_FAIL: "Socket Connection Failed"
});