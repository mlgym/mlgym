import { createEntityAdapter, createSlice, EntityState, PayloadAction } from "@reduxjs/toolkit";
import { ChartUpdate } from "../../worker_socket/event_handlers/EvaluationResultHandler";
import { RootState } from "../store";

interface Experiment {
    exp_id: number,
    data: Array<number>,
}

export interface Chart {
    chart_id: string,
    x_axis: Array<number>,
    experiments: EntityState<Experiment>,
}

const chartsAdapter = createEntityAdapter<Chart>({
    selectId: ({ chart_id }: Chart) => chart_id,
});

const experimentsAdapter = createEntityAdapter<Experiment>({
    selectId: ({ exp_id }: Experiment) => exp_id,
});

const initialState: EntityState<Chart> = chartsAdapter.getInitialState({});

export const chartsSlice = createSlice({
    name: 'charts',
    initialState,
    reducers: {
        upsertCharts(state, { payload }: PayloadAction<ChartUpdate[]>) {
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
                        const experiment: Experiment = {
                            exp_id: exp_id,
                            data: [score]
                        };
                        experimentsAdapter.addOne(chart.experiments, experiment);
                    }
                } else {
                    const chart: Chart = {
                        chart_id: chart_id,
                        x_axis: [epoch],
                        experiments: experimentsAdapter.getInitialState({
                            // adding the experiment manually because "experimentsAdapter.addOne" didn't work!
                            ids: [exp_id],
                            entities: {
                                [exp_id]: {
                                    exp_id: exp_id,
                                    data: [score]
                                }
                            },
                        })
                    };
                    chartsAdapter.addOne(state, chart);
                    // NOTE: "experimentsAdapter.addOne" didn't work and I couldn't figure out why?
                    // const experiment: Experiment = {
                    //     exp_id: exp_id,
                    //     data: [score]
                    // };
                    // experimentsAdapter.addOne(state.entities[chart_id]!.experiments, experiment);
                    // console.log(state.entities[chart_id]!.experiments, experiment); //Testing shows it doesn't get added!
                }
            }
        },
    }
});

export const { upsertCharts } = chartsSlice.actions;

// TODO: memoize these selectors
export const selectChartLabelsById = (state: RootState, chart_id: string) => state.charts.entities[chart_id]?.x_axis ?? [];
export const selectExperimentsPerChartById = (state: RootState, chart_id: string) => state.charts.entities[chart_id]?.experiments.entities ?? {};


// create a set of memoized selectors
export const {
    selectIds: selectChartIds,
    selectTotal: selectChartsCount,
} = chartsAdapter.getSelectors((state: RootState) => state.charts)

export default chartsSlice.reducer;