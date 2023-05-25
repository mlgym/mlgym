import { createEntityAdapter, createSlice, EntityState, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../store";


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

const initialState: EntityState<Row> = rowsAdapter.getInitialState({});

export const tableSlice = createSlice({
    name: 'table',
    initialState,
    reducers: {
        // NOTE: when multiple updates targets the same ID, they will be merged into a single update,
        // with later updates overwriting the earlier ones. So can't use the line below:
        // upsertManyRows: rowsAdapter.upsertMany,
        // https://redux-toolkit.js.org/api/createEntityAdapter#applying-multiple-updates
        upsertManyRows: (state, { payload }: PayloadAction<Row[]>) => {
            // TODO: instead of looping here over a potentially large array
            // in the background thread we can only send the last updates base on every event type, and overwrite the state here!
            for (let i = 0; i < payload.length; i++) {
                state = rowsAdapter.upsertOne(state, payload[i]);
                // if (payload[i].experiment_id in state.entities) {
                //     state = rowsAdapter.updateOne(state, { id: payload[i].experiment_id, changes: payload[i] } as Update<Row>);
                // } else {
                //     // add it directly
                //     state = rowsAdapter.addOne(state, payload[i]);
                // }
            }
        }
    }
});


export const { upsertManyRows } = tableSlice.actions;

// create a set of memoized selectors
export const {
    selectAll: selectAllRows,
    selectById: selectRowById
} = rowsAdapter.getSelectors((state: RootState) => state.table)

export default tableSlice.reducer;