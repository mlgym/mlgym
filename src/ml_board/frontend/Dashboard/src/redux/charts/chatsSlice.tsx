import { createEntityAdapter, createSlice } from "@reduxjs/toolkit";
import { RootState } from "../store";


const chartsAdapter = createEntityAdapter({});

// interface ChartsState {
//     // The unique IDs of each chart.
//     ids: [];
//     // A lookup table mapping chart IDs to the corresponding chart objects
//     entities: {};
// }

const initialState = chartsAdapter.getInitialState({});

export const chartsSlice = createSlice({
    name: 'charts',
    initialState,
    reducers: {
        upsertChart: chartsAdapter.upsertOne //(state, action.payload);
    }
});


export const { upsertChart } = chartsSlice.actions;

// create a set of memoized selectors
export const {
    selectIds: selectChartIds,
    selectEntities: selectCharts,
    selectTotal : selectChartsCount,
} = chartsAdapter.getSelectors((state: RootState) => state.charts)

export default chartsSlice.reducer;