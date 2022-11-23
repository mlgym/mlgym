import Chart                from "./Chart";
import { store            } from "../../app/store";
import { selectExperiment } from "../../features/experiments/experimentsSlice";
import "./Charts.scss";

interface SplitMetricExp {
  [split_metric: string]: string[]; // Array of exp ids
}

function Charts({eIDs}: {eIDs: string[]}) {
  let charts: JSX.Element[] = [];

  // Map split_metric ids to an array of experiment ids
  let SMMap: SplitMetricExp = {};
  for (let iExpID = 0; iExpID < eIDs.length; iExpID++) {
    let curExp = selectExperiment (store.getState (), eIDs[iExpID]);
    if (curExp !== undefined && curExp.chart_ids !== undefined) {
      for (let iChartTitle = 0; iChartTitle < curExp.chart_ids.length; iChartTitle++) {
        let mapKey = curExp.chart_ids[iChartTitle];
        let mapVal = SMMap[mapKey] || [];
        mapVal.push (curExp.experiment_id);
        mapVal = [ ...new Set (mapVal) ];
        SMMap[mapKey] = mapVal;
      }
    }
  }

  let mapKeys = Object.keys (SMMap);
  for (let iKey = 0; iKey < mapKeys.length; iKey++) {
    let curKey  = mapKeys[iKey];
    let curEIDs = SMMap[curKey];
    if (curEIDs !== undefined) {
      let chart: JSX.Element = (
        <div className="chart" key={`chart#${curKey}`}>
          <div className="title">{curKey}</div>
          <Chart eIDs={curEIDs} split_metric={curKey} />
        </div>
      );

      charts.push (chart);
    }
  }

  return (
    <div className='charts'>
      {charts}
    </div>
  )
}

export default Charts;