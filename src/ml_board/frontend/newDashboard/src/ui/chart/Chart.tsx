import React, { ReactNode          } from "react";
import { useState                  } from "react";
import { LineChart                 } from "recharts";
import { ResponsiveContainer       } from "recharts";
import { CartesianGrid             } from "recharts";
import { XAxis                     } from "recharts";
import { YAxis                     } from "recharts";
import { Tooltip                   } from "recharts";
import { Legend                    } from "recharts";
import { Line                      } from "recharts";
import { Props   as LegendProps    } from "recharts/types/component/DefaultLegendContent";
import { Payload as LegendPayload  } from "recharts/types/component/DefaultLegendContent";
import { ValueType                 } from "recharts/types/component/DefaultTooltipContent";
import { NameType                  } from "recharts/types/component/DefaultTooltipContent";
import { Props   as TooltipProps   } from "recharts/types/component/DefaultTooltipContent"; 
import { Payload as TooltipPayload } from "recharts/types/component/DefaultTooltipContent";
import { store                     } from "../../app/store";
import { Epoch                     } from "../../features/experiments/experimentsSlice";
import { selectExperiment          } from "../../features/experiments/experimentsSlice";
import "./Chart.scss";

function Chart ({eIDs, split_metric}: {eIDs: string[], split_metric: string}) {
  const [activeLine, setActiveLine] = useState ('');
  let lines: JSX.Element[] = [];

  for (let iExpID = 0; iExpID < eIDs.length; iExpID++) {
    let e = selectExperiment (store.getState (), eIDs[iExpID]);

    if (e !== undefined) {
      let linePoints = e[split_metric] as Epoch[];
      let lineKey    = `exp#${iExpID}`;

      lines.push (
        <Line key={lineKey} type="monotone"
              dataKey={e.experiment_id} data={linePoints}
              dot={false} activeDot={false} strokeWidth={1.2}
              stroke={e.color} strokeOpacity={(activeLine === lineKey || !activeLine.length) ? 1 : 0} />
      )
    }
  }
    
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart onMouseLeave={() => setActiveLine ('')}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="id" allowDuplicatedCategory={false} />
        <YAxis />
        <Tooltip content={renderTooltip} />
        <Legend  content={(props: LegendProps) => renderLegend (props, setActiveLine)} verticalAlign="bottom" />
        {lines}
      </LineChart>
    </ResponsiveContainer>
  )
}

const renderLegend = (props: LegendProps, setActiveLine: React.Dispatch<React.SetStateAction<string>>): ReactNode => {
  const { payload } = props;
  if (!payload) return <></>;

  return (
    <div className="legendsContainer">
      <div className="chartLegends" onMouseLeave={() => setActiveLine ('')}>
        {
          payload.map (
            (entry: LegendPayload, index: number) => (
              <span key={`legend#${index}`} className="legendVal"
                    style={{ borderColor: entry.color, cursor: "pointer" }}
                    onMouseEnter={() => setActiveLine (`exp#${index}`)} >
                {entry.value}
              </span>
            )
          )
        }
      </div>
    </div>
  );
}

const renderTooltip = (props: TooltipProps<ValueType, NameType>): ReactNode => {
  if (props.payload && props.payload.length) {
    return (
      <div className="chartTooltip">
        <div className="tooltipHeader">Epoch# {props.label}</div>
        <div className="tooltipValues">
          {
            props.payload.map (
              (entry: TooltipPayload<ValueType, NameType>, idx: number) => {
                if (typeof (entry.value) !== 'number') return <></>;
                return (
                  <span key={`tooltip#${idx}`} className="tooltipVal" style={{ borderColor: entry.color }}>
                    {Math.round (entry.value * 1000) / 1000}
                  </span>
                )
              }
            )
          }
        </div>
      </div>
    );
  }

  return null;
}

export default Chart;