import { useAppSelector } from "../../app/hooks";
import { selectExperiments } from "../../redux/experiments/yetAnotherExperimentSlice";
import { selectAllJobs } from "../../redux/jobs/jobSlice";
import { selectColorMap, selectFilter } from "../../redux/status/statusSlice";
import Table from "./table/Table";


interface TableRow {
  // Job
  job_id: string; // format <grid_search_id>-<job index>
  job_type: string; // <CALC, TERMINATE>
  job_status: string; // <INIT, RUNNING, DONE>
  starting_time: number;
  finishing_time: number;
  error: string;
  stacktrace: string;
  device: string;
  // Experiment
  experiment_id: number;
  model_status?: string;   // <TRAINING, EVALUATING>,
  current_split?: string;
  splits?: string[]; //e.g.: ["train", "val", "test"],
  num_epochs?: number;
  current_epoch?: number;
  num_batches?: number;
  current_batch?: number;
  // special Experiment keys for "latest_split_metric"
  F1?: string;
  Precision?: string;
  Recall?: string;
  // calculations
  epoch_progress?: number;
  batch_progress?: number;
  // TODO: maybe get color???
  color?: string;
}


export default function Dashboard() {
  // filter them based on the regEx in the status slice
  const re = new RegExp(useAppSelector(selectFilter));
  const colorMap = useAppSelector(selectColorMap);

  // prepare array for rows
  const rows: TableRow[] = [];

  // get all Job[] and Dictionary<Experiment>
  const jobs = useAppSelector(selectAllJobs);
  const experiments = useAppSelector(selectExperiments);
  // loop over all job
  for (const job of jobs) {

    // create a table row with the job
    let row: TableRow = { ...job };

    // get the experiment and do the needed progress calculations
    const expID = job.experiment_id;
    const experiment = experiments[expID];
    // NOTE: assumption is if the experiment is there then all it's values exist as well
    if (experiment !== undefined) {
      // calc the progresses here for better code readablity 
      // TODO: epochs can appear as they are not in % but rather just the epoch's number
      let epoch_progress = experiment.current_epoch / experiment.num_epochs;
      let batch_progress = experiment.current_batch / experiment.num_batches;

      // // if the scores/"latest_split_metric" needs handling before showing them in the table? (I don't think so)
      // const scores = {
      //   F1: experiment.F1 as string,
      //   Precision: experiment.Precision as string,
      //   Recall: experiment.Recall as string,
      // }

      // add the experiment to the row
      row = { ...row, ...experiment, epoch_progress, batch_progress }
    }
    
    rows.push(row);
  }
  // console.log(rows.at(-1));

  // TODO: get the names of the metric and the loss only, as the rest stays the same!
  // IMPORTANT NOTE: these names have to match the keys of the row object exactly in order to appear in the table
  const colNames_old = ["job_id", "job_type", "job_status", "experiment_id", "starting_time", "finishing_time",
    "epoch_progress", "batch_progress", "model_status", "current_split", "splits", "error",
    "stacktrace", "device", "current_epoch", "num_epochs", "train_F1_SCORE_macro", "train_PRECISION_macro",
    "train_RECALL_macro", "train_cross_entropy_loss", "val_F1_SCORE_macro", "val_PRECISION_macro", "val_RECALL_macro",
    "val_cross_entropy_loss", "test_F1_SCORE_macro", "test_PRECISION_macro", "test_RECALL_macro", "test_cross_entropy_loss"];

  const colNames = ["job_id", "job_status", "experiment_id", "starting_time", "finishing_time",
  "train_cross_entropy_loss", "val_cross_entropy_loss", "test_cross_entropy_loss"];

  return (<Table colNames={colNames.filter((colName: string) => re.test(colName))} rows={rows} />);
}