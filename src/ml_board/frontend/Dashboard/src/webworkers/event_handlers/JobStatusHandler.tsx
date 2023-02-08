import { Job } from "../../redux/jobs/jobSlice";

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


// data should be like Job but I'm chaning the key name from "status" to "job_status"
export default function handleJobStatusData(data: any): Job {
    data.job_status = data.status;
    delete data.status
    return data;
}