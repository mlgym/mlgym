import { Toolbar } from '@mui/material';
import { useAppSelector } from "../../app/hooks";
import { selectFilter, selectTableHeaders } from "../../redux/status/statusSlice";
import { selectAllRows } from "../../redux/table/tableSlice";
import Table from "./table/Table";


export default function Dashboard() {
  // filter them based on the regEx in the status slice
  const re = new RegExp(useAppSelector(selectFilter));
  // const colorMap = useAppSelector(selectColorMap);
  const rows = useAppSelector(selectAllRows);
  const colNames: string[] = useAppSelector(selectTableHeaders);

  // Table should consist of these columns for minimized view. To get detailed view, user can click on the row and see the job + experiment details:
  // const colNames = ["experiment_id", "job_status", "starting_time", "finishing_time",
  // "model_status", "epoch_progress", "batch_progress"];


  return (
    <div>
      <Toolbar />
      <Table colNames={colNames.filter((colName: string) => re.test(colName))} rows={rows} />
    </div>
  );
}