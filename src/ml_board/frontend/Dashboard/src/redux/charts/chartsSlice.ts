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
                if (chart_id in state.entities) { //if (state.entities[chart_id] !== undefined)
                    const chart = state.entities[chart_id] as Chart;
                    // update X-axis
                    if (!(epoch in chart.x_axis)) // if (chart.x_axis[epoch] != epoch)
                        chart.x_axis.push(epoch)
                    // if experiment exists, push the score, otherwise add it as new
                    if (exp_id in chart.experiments.entities) { //if (chart.experiments.entities[exp_id] !== undefined)
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
export const selectChartsByExperimentId = (state: RootState, exp_id: string) =>{
    const allExp: {[key: string]: any} = {};
    for (const chart_id in state.charts.entities) {
        const experiments = state.charts.entities[chart_id]?.experiments.entities ?? {};
        if(experiments[exp_id]) {
            allExp[chart_id] = experiments[exp_id];
        }
    }
    return allExp;
}

// create a set of memoized selectors
export const {
    selectIds: selectChartIds,
    selectTotal: selectChartsCount,
} = chartsAdapter.getSelectors((state: RootState) => state.charts)

export default chartsSlice.reducer;