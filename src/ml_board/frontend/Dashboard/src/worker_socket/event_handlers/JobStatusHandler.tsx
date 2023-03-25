
// interface data_job_status {
//     "job_id": "2022-11-23--20-08-38-17",
//     "job_type": 1,
//     "status": "RUNNING",
//     "grid_search_id": "2022-11-23--20-08-38",
//     "experiment_id": 17,
//     "starting_time": 1669234123.8701758,
//     "finishing_time": -1,
//     "device": "cuda:4",
//     "error": null,
//     "stacktrace": null
// }


export interface JobStatusRefinedPayload {
    job_id: string; // format <grid_search_id>-<job index>
    job_type: string; // <CALC, TERMINATE>
    job_status: string; // <INIT, RUNNING, DONE>
    // grid_search_id: string;
    experiment_id: number;
    starting_time: number;
    finishing_time: number;
    error: string;
    stacktrace: string;
    device: string;
}

export default function handleJobStatusData(jobData: any): JobStatusRefinedPayload {
    // key renaming "status" to "job_status"
    jobData.job_status = jobData.status;
    delete jobData.status

    // remove grid_search_id
    delete jobData.grid_search_id

    return jobData;
}