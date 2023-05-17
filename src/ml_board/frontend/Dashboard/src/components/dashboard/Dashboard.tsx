import { useAppSelector } from "../../app/hooks";
import { selectFilter } from "../../redux/status/statusSlice";
import { selectAllRows } from "../../redux/table/tableSlice";
import Table from "./table/Table";
import { Toolbar } from '@mui/material';

export interface TableRow {
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
  // const colorMap = useAppSelector(selectColorMap);
  const rows = useAppSelector(selectAllRows);
  const colNames: string[] = [];

  // Table should consist of these columns for minimized view. To get detailed view, user can click on the row and see the job + experiment details:
  // const colNames = ["experiment_id", "job_status", "starting_time", "finishing_time",
  // "model_status", "epoch_progress", "batch_progress"];

  // TODO: get them from the Redux store better, otherwise this checks the first row ONLY!!!
  // getting the columns' headers dynamically
  if (rows.length > 1) {
    colNames.push(...Object.keys(rows[0]).filter((colName: string) => re.test(colName)));
  }

  return (
    <div>
      <Toolbar />
      <Table colNames={colNames} rows={rows} />
    </div>
  );
}