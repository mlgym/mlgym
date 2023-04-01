import { useAppSelector } from "../../app/hooks";
import { selectFilter } from "../../redux/status/statusSlice";
import { selectAllRows } from "../../redux/table/tableSlice";
import Table from "./table/Table";


export default function Dashboard() {
  // filter them based on the regEx in the status slice
  const re = new RegExp(useAppSelector(selectFilter));
  // const colorMap = useAppSelector(selectColorMap);
  const rows = useAppSelector(selectAllRows);
  const colNames: string[] = [];

  // TODO: get them from the Redux store better, otherwise this checks the first row ONLY!!!
  // getting the columns' headers dynamically
  if (rows.length > 1) {
    colNames.push(...Object.keys(rows[0]).filter((colName: string) => re.test(colName)));
  }

  return (<Table colNames={colNames} rows={rows} />);
}