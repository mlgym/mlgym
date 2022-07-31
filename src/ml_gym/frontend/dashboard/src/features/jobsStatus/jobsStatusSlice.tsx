import { createSlice } from '@reduxjs/toolkit'
import { JobStatusType } from '../../app/datatypes'


const initialState = [
    // {
    //     "event_id": 0,
    //     "data": {
    //         "event_type": "job_status",
    //         "creation_ts": 1659089129,
    //         "payload": { "job_id": 1, "job_type": 'CALC', "current_status": 'INIT', "experiment_id": "1/1", "starting_time": -1, "finishing_time": -1 },
    //     }
    // } as JobStatusType
] as Array<JobStatusType>





const jobsStatusSlice = createSlice({
    name: 'jobsStatus',
    initialState,
    reducers: {
        jobStatusAdded(state, action) {
            state.push(action.payload)
        }
    }
})

export const { jobStatusAdded } = jobsStatusSlice.actions
export default jobsStatusSlice.reducer