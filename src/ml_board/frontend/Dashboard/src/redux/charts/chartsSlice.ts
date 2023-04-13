import { createEntityAdapter, createSlice, EntityState, PayloadAction } from "@reduxjs/toolkit";
import { ChartUpdate } from "../../worker_socket/event_handlers/EvaluationResultHandler";
import { RootState } from "../store";

interface Experiment {
    exp_id: number,
    data: Array<number>,
}

export interface Chart {
    chart_id: string,
    x_axis: Array<number>, // Array<string>, // in Graph.tsx parsing: false, 
    experiments: EntityState<Experiment>,
}

const chartsAdapter = createEntityAdapter<Chart>({
    selectId: ({ chart_id }: Chart) => chart_id,
    sortComparer: ({ chart_id: id1 }: Chart, { chart_id: id2 }: Chart) => id1.localeCompare(id2)
});

const experimentsAdapter = createEntityAdapter<Experiment>({
    selectId: ({ exp_id }: Experiment) => exp_id,
    sortComparer: ({ exp_id: id1 }: Experiment, { exp_id: id2 }: Experiment) => id1 - id2
});

const initialState: EntityState<Chart> = chartsAdapter.getInitialState({});

export const chartsSlice = createSlice({
    name: 'charts',
    initialState,
    reducers: {
        upsertCharts(state, { payload }: PayloadAction<ChartUpdate[]>) {
            // TODO: avoid this big loop !!!
            for (const chartUpdate of payload) {
                const { chart_id, exp_id, epoch, score } = chartUpdate;
                if (state.ids.includes(chart_id)) {
                    const chart = state.entities[chart_id] as Chart;
                    // update X-axis
                    if (!chart.x_axis.includes(epoch))
                        chart.x_axis.push(epoch)
                    // if experiment exist push the score otherwise add it as new
                    if (chart.experiments.ids.includes(exp_id)) {
                        (chart.experiments.entities[exp_id] as Experiment).data.push(score);
                    } else {
                        chart.experiments = experimentsAdapter.addOne(chart.experiments, {
                            exp_id: exp_id,
                            data: [score]
                        } as Experiment);
                    }
                } else {
                    const chart: Chart = {
                        chart_id: chart_id,
                        x_axis: [epoch],
                        experiments: experimentsAdapter.getInitialState()
                    };
                    chartsAdapter.addOne(state, chart);
                    chart.experiments = experimentsAdapter.addOne(chart.experiments, {
                        exp_id: exp_id,
                        data: [score]
                    } as Experiment);
                }
            }
        },
    }
});

export const { upsertCharts } = chartsSlice.actions;

// TODO: memoize these selectors
export const selectChartLabelsById = (state: RootState, chart_id: string) => state.charts.entities[chart_id]?.x_axis ?? [];
export const selectExperimentsPerChartById = (state: RootState, chart_id: string) => state.charts.entities[chart_id]?.experiments.entities ?? {};
// export const fun = (state: RootState, exp_id: string) =>{
//     const allExp = {};
//     for (const chart_id in state.charts.entities) {
//         const experiments = state.charts.entities[chart_id]?.experiments.entities ?? {};
//         allExp[chart_id] = experiments[exp_id];
//     }
//     return allExp;
// }

// create a set of memoized selectors
export const {
    selectIds: selectChartIds,
    selectTotal: selectChartsCount,
} = chartsAdapter.getSelectors((state: RootState) => state.charts)

export default chartsSlice.reducer;