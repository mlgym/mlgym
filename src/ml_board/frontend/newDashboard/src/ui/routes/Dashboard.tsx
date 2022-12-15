import { useAppSelector } from "../../app/hooks";
import { store } from "../../app/store";
import { selectExperiment } from "../../features/experiments/experimentsSlice";
import { selectJobs } from "../../features/jobs/jobsSlice";
import { selectFilter } from "../../features/status/statusSlice";

import Table from "../table/Table";

interface TableRow {
  experiment_id: string;
  job_id: string;               // format <grid_search_id>-<job index>
  job_type?: string;            // <CALC, TERMINATE>
  job_status?: string;          // <INIT, RUNNING, DONE>
  starting_time?: number;
  finishing_time?: number;
  error?: string;
  stacktrace?: string;
  device?: string;
  model_status?: string;        // <TRAINING, EVALUATING>,
  current_split?: string;
  num_epochs?: number;
  current_epoch?: number;
  num_batches?: number;
  current_batch?: number;

  epoch_progress?: number;
  batch_progress?: number;

  color?: string;
  splits?: string[];           //e.g.: ["train", "val", "test"],
}


function Dashboard() {

  // filter them based on the regEx in the status slice
  const re = new RegExp(useAppSelector(selectFilter))

  // get the jobs
  const jobs = useAppSelector(selectJobs);

  // prepare array for rows
  const rows: TableRow[] = [];

  // loop over the jobs skipping the job without an experiment
  for (const job of Object.values(jobs)) {
    if (job.experiment_id === undefined)
      continue;

    // get the assigned experiment
    const experiment = selectExperiment(store.getState(), job.experiment_id)
    if (experiment === undefined)
      continue;

    // calc the progresses here for better code readablity 
    let epoch_progress = -1;
    if (experiment.current_epoch !== undefined && experiment.num_epochs !== undefined) {
      epoch_progress = experiment.current_epoch / experiment.num_epochs;
    }
    let batch_progress = -1;
    if (experiment.current_batch !== undefined && experiment.num_batches !== undefined) {
      epoch_progress = experiment.current_batch / experiment.num_batches;
    }

    // TODO: add the metrics to the row

    // add the row to the rows
    rows.push({
      experiment_id: job.experiment_id,
      job_id: job.job_id,
      job_type: job.job_type,
      job_status: job.status,
      starting_time: job.starting_time,
      finishing_time: job.finishing_time,
      error: job.error,
      stacktrace: job.stacktrace,
      device: job.device,
      model_status: experiment.status,
      current_split: experiment.current_split,
      num_epochs: experiment.num_epochs,
      current_epoch: experiment.current_epoch,
      num_batches: experiment.num_batches,
      current_batch: experiment.current_batch,
      epoch_progress: epoch_progress,
      batch_progress: batch_progress,
      color: experiment.color,
      splits: experiment.splits,
    });
  }

  // TODO: get the colNames from the experiment slice and job slice keys, in a better way?! maybe?!
  const colNames = ["job_id", "job_type", "job_status", "experiment_id", "starting_time", "finishing_time",
    "epoch_progress", "batch_progress", "model_status", "current_split", "splits", "error",
    "stacktrace", "device", "current_epoch", "num_epochs", "f1_score_macro", "precision_macro", "recall_macro"]

  return (
    <Table colNames={colNames.filter((colName: string) => re.test(colName))} rows={rows} />
  )
}

export default Dashboard;