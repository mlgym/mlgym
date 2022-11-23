import { Job } from './jobsSlice';

export interface serverJob {
  job_id        : string;
  [key: string] : any;
}

export type jobEvent = "job_scheduled" | "job_status";

export const convertJob = (input: serverJob, eType: jobEvent): Job => {
  if (input["job_id"] === undefined) throw ("Missing identifier in message 'job_id'");

  let result: Job = {
    job_id : ""
  }

  switch (eType) {
    case "job_scheduled": {
      // no example provided.
      console.log ("NANI?!");
    } break;


    /*
    "payload": { 
      "job_id"         : <int>
      "job_type"       : <CALC, TERMINATE>
      "status"         : <INIT, RUNNING, DONE>
      "grid_search_id" : <timestamp>,
      "experiment_id"  : <int>
      "starting_time"  : <int>
      "finishing_time" : <int>
      "error"          : <string>
      "stacktrace"     : <string>
      "device"         : <string>
    }
    */
    case "job_status": {
      result = {
        job_id         : input.job_id,
        job_type       : input.job_type,
        status         : input.status,
        grid_search_id : input.grid_search_id, 
        experiment_id  : input.experiment_id,
        starting_time  : input.starting_time,
        finishing_time : input.finishing_time,
        error          : input.error,
        stacktrace     : input.stacktrace,
        device         : input.device
      }
    } break;

    default: break;
  }

  return result;
}
