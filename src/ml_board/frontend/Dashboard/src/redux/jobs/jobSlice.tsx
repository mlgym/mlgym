import { createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
import { RootState } from "../store";


// A.K.A JobStatusPayload
export interface Job {
    job_id: string; // format <grid_search_id>-<job index>
    job_type: string; // <CALC, TERMINATE>
    job_status: string; // <INIT, RUNNING, DONE>
    // grid_search_id: string;
    experiment_id: number;
    starting_time: number;
    finishing_time: number;
    error: string;
    stacktrace: string;
    device: string;
}

const jobsAdapter = createEntityAdapter<Job>({
    selectId: ({ job_id }: Job) => job_id,
    sortComparer: ({ job_id: id1 }: Job, { job_id: id2 }: Job) => id1.localeCompare(id2),
});

// interface JobsState {
//     // The unique IDs of each job.
//     ids: [];
//     // A lookup table mapping job IDs to the corresponding Job objects
//     entities: {};
// }

const initialState: EntityState<Job> = jobsAdapter.getInitialState({});

export const jobsSlice = createSlice({
    name: 'jobs',
    initialState,
    reducers: {
        upsertJob: jobsAdapter.upsertOne //(state, action.payload);
        // upsertJob: (state, action: PayloadAction<Job>) => {
        //     if (state[action.payload.job_id] === undefined) {
        //         state[action.payload.job_id] = action.payload
        //     } else {
        //         state[action.payload.job_id] = {
        //             ...state[action.payload.job_id], ...action.payload
        //         };
        //     }
        // }
    }
});


export const { upsertJob } = jobsSlice.actions;

// create a set of memoized selectors
export const {
    // selectAll: selectAllJobs,
    selectById: selectJobById,
    selectIds: selectJobIds,
    selectAll: selectAllJobs,
} = jobsAdapter.getSelectors((state: RootState) => state.jobs)

export default jobsSlice.reducer;