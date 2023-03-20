import { Job } from "../../redux/jobs/jobSlice";

interface JobStatusPayload extends JSON {
    "job_id": string; // "2022-11-23--20-08-38-17",
    "job_type": string; // 1,
    "status": string; // "RUNNING",
    "grid_search_id": string; // "2022-11-23--20-08-38",
    "experiment_id": number; //  17,
    "starting_time": number; // 1669234123.8701758,
    "finishing_time": number; // -1,
    "device": string; // "cuda:4",
    "error": string; // null,
    "stacktrace": string; // null
}

// data should be like Job but I'm chaning the key name from "status" to "job_status"
export default function handleJobStatusData(data: JSON): Job {
    const { status, ...rest } = data as JobStatusPayload;
    return { job_status: status, ...rest };
}