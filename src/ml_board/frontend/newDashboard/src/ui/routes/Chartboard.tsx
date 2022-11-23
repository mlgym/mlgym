import { useAppSelector } from "../../app/hooks";
import { selectExperiments } from "../../features/experiments/experimentsSlice";
import Charts from "../chart/Charts";

function Chartboard() {
  let eIDs = Object.keys (useAppSelector (selectExperiments));

  return (
    <Charts eIDs={eIDs} />
  )
}

export default Chartboard;