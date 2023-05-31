import { createEntityAdapter, createSlice, EntityState, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../store";


interface TableHeaders {
    table_headers: Array<string>
}

// NOTE: Row = JobStatusPayload + ExperimentStatusPayload + scores
export interface Row {
    // // Job
    // job_id?: string; // format <grid_search_id>-<job index>
    // job_type?: string; // <CALC, TERMINATE>
    // job_status?: string; // <INIT, RUNNING, DONE>
    // starting_time?: number;
    // finishing_time?: number;
    // error?: string;
    // stacktrace?: string;
    // device?: string;
    // // Experiment
    experiment_id: number;
    // model_status?: string;   // <TRAINING, EVALUATING>,
    // current_split?: string;
    // splits?: string; //e.g.: ["train", "val", "test"],
    // num_epochs?: number;
    // current_epoch?: number;
    // num_batches?: number;
    // current_batch?: number;
    // // progresses calculations
    // epoch_progress?: number;
    // batch_progress?: number;
    // // special Experiment keys for "latest_split_metric"


    // NOTE: newKey encompasses all of the above and more if need be!!!
    // [newKey: string]: number | string;
    // But unfortunately it creates errors if used! (exposing only experiment_id is the current fix)
}

const rowsAdapter = createEntityAdapter<Row>({
    selectId: ({ experiment_id }: Row) => experiment_id,
    sortComparer: ({ experiment_id: id1 }: Row, { experiment_id: id2 }: Row) => id1 - id2
});

const initialState: EntityState<Row> & TableHeaders = rowsAdapter.getInitialState({
    table_headers: [],
});

const { actions, reducer } = createSlice({
    name: 'table',
    initialState,
    reducers: {
        // NOTE: when multiple updates targets the same ID, they will be merged into a single update, with later updates
        // overwriting the earlier ones. (https://redux-toolkit.js.org/api/createEntityAdapter#applying-multiple-updates)
        upsertManyRows: rowsAdapter.upsertMany,
        upsertTableHeaders: (state, { payload }: PayloadAction<string[]>) => {
            state.table_headers = [...new Set([...state.table_headers, ...payload])];
        }
    }
});


export const { upsertManyRows, upsertTableHeaders } = actions;

// create a set of memoized selectors
export const {
    selectAll: selectAllRows,
    selectById: selectRowById
} = rowsAdapter.getSelectors((state: RootState) => state.table)

export const selectTableHeaders = (state: RootState) => state.table.table_headers;

export default reducer;