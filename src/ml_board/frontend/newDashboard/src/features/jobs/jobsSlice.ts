import { createSlice   } from '@reduxjs/toolkit';
import { PayloadAction } from '@reduxjs/toolkit';
import { RootState     } from '../../app/store';

export interface Job {
  job_id          : string;
  job_type?       : string;
  status?         : string;
  grid_search_id? : string; 
  experiment_id?  : string;
  starting_time?  : number;
  finishing_time? : number;
  error?          : string;
  stacktrace?     : string;
  device?         : string;
}

export interface JobsState {
  [jID: string]: Job;
}

const initialState: JobsState = { }

export const jobsSlice = createSlice ({
  name: 'jobs',
  initialState,
  reducers: {
    upsertJob: (state, action: PayloadAction<Job>) => {
      if (state[action.payload.job_id] === undefined) {
        state[action.payload.job_id] = action.payload
      } else {
        state[action.payload.job_id] = {
          ...state[action.payload.job_id], ...action.payload
        };
      }
    }
  }
});

export const { upsertJob } = jobsSlice.actions;
export const selectJobs = (state: RootState) => state.jobs;
export default jobsSlice.reducer;