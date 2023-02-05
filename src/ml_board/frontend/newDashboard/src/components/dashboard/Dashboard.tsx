import { useAppSelector } from "../../app/hooks";
import { Experiment, selectExperiments } from "../../redux/experiments/yetAnotherExperimentSlice";
import { selectAllJobs } from "../../redux/jobs/jobSlice";
import { selectColorMap, selectFilter } from "../../redux/status/statusSlice";
import Table from "./table/Table";


interface TableRow {
  // Job
  job_id: string; // format <grid_search_id>-<job index>
  job_type?: string; // <CALC, TERMINATE>
  job_status?: string; // <INIT, RUNNING, DONE>
  starting_time?: number;
  finishing_time?: number;
  error?: string;
  stacktrace?: string;
  device?: string;
  // Experiment
  experiment_id: string;
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
    const expID = job.experiment_id as string;
    const experiment = experiments[expID] as Experiment;
    if (experiment !== undefined) {
      // calc the progresses here for better code readablity 
      let epoch_progress = -1;
      if (experiment.current_epoch !== undefined && experiment.num_epochs !== undefined) {
        epoch_progress = experiment.current_epoch / experiment.num_epochs;
      }
      let batch_progress = -1;
      if (experiment.current_batch !== undefined && experiment.num_batches !== undefined) {
        epoch_progress = experiment.current_batch / experiment.num_batches;
      }
    }

    // // if the scores/"latest_split_metric" needs handling before showing them in the table? (I don't think so)
    // const scores = {
    //   F1: experiment.F1 as string,
    //   Precision: experiment.Precision as string,
    //   Recall: experiment.Recall as string,
    // }

    // create the TableRow and push it
    rows.push({
      ...job,
      ...experiment,
      // epoch_progress: epoch_progress,
      // batch_progress: batch_progress,
      // color: colorMap[experiment.experiment_id],
      // ...scores
    });
  }
  console.log(rows.at(-1));



  // // loop over all job ids
  // const job_ids = useAppSelector(selectJobIds);
  // for (const jID of job_ids) {
  //   // get job and the experiment
  //   const job: Job = useAppSelector(state => selectJobById(state, jID)) as Job;
  //   const expID = job.experiment_id as string;
  //   const experiment: Experiment = useAppSelector(state => selectExperimentById(state, expID)) as Experiment;

  //   // calc the progresses here for better code readablity 
  //   let epoch_progress = -1;
  //   if (experiment.current_epoch !== undefined && experiment.num_epochs !== undefined) {
  //     epoch_progress = experiment.current_epoch / experiment.num_epochs;
  //   }
  //   let batch_progress = -1;
  //   if (experiment.current_batch !== undefined && experiment.num_batches !== undefined) {
  //     epoch_progress = experiment.current_batch / experiment.num_batches;
  //   }

  //   // // if the scores/"latest_split_metric" needs handling before showing them in the table? (I don't think so)
  //   // const scores = {
  //   //   F1: experiment.F1 as string,
  //   //   Precision: experiment.Precision as string,
  //   //   Recall: experiment.Recall as string,
  //   // }

  //   // create the TableRow and push it
  //   rows.push({
  //     ...job,
  //     ...experiment,
  //     epoch_progress: epoch_progress,
  //     batch_progress: batch_progress,
  //     color: colorMap[experiment.experiment_id],
  //     // ...scores
  //   });
  // }


  // REMOVED because the type 'undefined' is not a valid JSX element
  // // TODO: this might be redundant???
  // const iActiveTab = useAppSelector(selectTab);
  // if ("Dashboard" !== iActiveTab)
  //   return;

  // TODO: get the colNames from the redux state ???
  // IMPORTANT NOTE: these names have to match the keys of the row object exactly in order to appear in the table
  const colNames = ["job_id", "job_type", "job_status", "experiment_id", "starting_time", "finishing_time",
    "epoch_progress", "batch_progress", "model_status", "current_split", "splits", "error",
    "stacktrace", "device", "current_epoch", "num_epochs", "F1", "Precision", "Recall"];

  return (
    <div>
      Dashboard
      <Table colNames={colNames.filter((colName: string) => re.test(colName))} rows={rows} />
    </div>
  );
}