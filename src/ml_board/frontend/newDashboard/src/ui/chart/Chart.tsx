import { LineChart           } from "recharts";
import { ResponsiveContainer } from "recharts";
import { CartesianGrid       } from "recharts";
import { XAxis               } from "recharts";
import { YAxis               } from "recharts";
import { Tooltip             } from "recharts";
import { Legend              } from "recharts";
import { Line                } from "recharts";
import { store               } from "../../app/store";
import { Epoch               } from "../../features/experiments/experimentsSlice";
import { selectExperiment    } from "../../features/experiments/experimentsSlice";
import "./Chart.scss";

function Chart ({eIDs, split_metric}: {eIDs: string[], split_metric: string}) {
  let lines: JSX.Element[] = [];

  for (let iExpID = 0; iExpID < eIDs.length; iExpID++) {
    let e = selectExperiment (store.getState (), eIDs[iExpID]);

    if (e !== undefined) {
      let linePoints = e[split_metric] as Epoch[];
      let lineData: any[] = [];
      for (let iPoint = 0; iPoint < linePoints.length; iPoint++) {
        let currentPoint = linePoints[iPoint];
        let curObj = { name: Number (currentPoint.id), [e.experiment_id]: Number (currentPoint.score) };
        lineData.push (curObj);
      }

      lines.push (
        <Line key={`line#${iExpID}`} type="monotone" dataKey={e.experiment_id} data={lineData} />
      )
    }
  }
    
  return (
    <ResponsiveContainer width="100%" height="100%" >
      <LineChart>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" allowDuplicatedCategory={false} />
        <YAxis />
        <Tooltip />
        <Legend />
        {lines}
      </LineChart>
    </ResponsiveContainer>
  )
}

export default Chart;