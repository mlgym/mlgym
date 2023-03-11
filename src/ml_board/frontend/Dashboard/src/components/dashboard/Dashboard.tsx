import { useAppSelector } from "../../app/hooks";
import { selectColorMap, selectFilter } from "../../redux/status/statusSlice";
import { selectAllRows } from "../../redux/table/tableSlice";
import Table from "./table/Table";


// TODO: Maybe merge table and Dashboard?
export default function Dashboard() {
  // filter them based on the regEx in the status slice
  const re = new RegExp(useAppSelector(selectFilter));
  const colorMap = useAppSelector(selectColorMap);
  const rows = useAppSelector(selectAllRows);
  const colNames: string[] = [];

  // TODO: get them from the Redux store
  // getting the columns' headers dynamically
  if (rows.length > 1) {
    colNames.push(...Object.keys(rows[0]).filter((colName: string) => re.test(colName)));
  }

  // // TODO: get the names of the metric and the loss only, as the rest stays the same!
  // // IMPORTANT NOTE: these names have to match the keys of the row object exactly in order to appear in the table
  // const colNames = ["job_id", "job_type", "job_status", "experiment_id", "starting_time", "finishing_time",
  //   "epoch_progress", "batch_progress", "model_status", "current_split", "splits", "error",
  //   "stacktrace", "device", "current_epoch", "num_epochs", "train_F1_SCORE_macro", "train_PRECISION_macro",
  //   "train_RECALL_macro", "train_cross_entropy_loss", "val_F1_SCORE_macro", "val_PRECISION_macro", "val_RECALL_macro",
  //   "val_cross_entropy_loss", "test_F1_SCORE_macro", "test_PRECISION_macro", "test_RECALL_macro", "test_cross_entropy_loss"];


  return (<Table colNames={colNames} rows={rows} />);
}