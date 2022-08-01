import { createSlice } from '@reduxjs/toolkit'
import { JobStatusMessageCollectionType } from '../../app/datatypes'


const initialState = {
    messages: [],
    job_id_to_latest_message_index: {}
    // {
    //     "event_id": 0,
    //     "data": {
    //         "event_type": "job_status",
    //         "creation_ts": 1659089129,
    //         "payload": { "job_id": 1, "job_type": 'CALC', "status": 'INIT', "experiment_id": "1/1", "starting_time": -1, "finishing_time": -1 },
    //     }
    // } as JobStatusType
} as JobStatusMessageCollectionType




const jobsStatusSlice = createSlice({
    name: 'jobsStatus',
    initialState,
    reducers: {
        jobStatusAdded(state, action) {
            const job_id: number = action.payload.data.payload.job_id
            if (job_id in state.job_id_to_latest_message_index) {
                const row_id = state.job_id_to_latest_message_index[job_id]
                // prevents possible race condition
                if (state.messages[row_id].event_id < action.payload.event_id) {
                    state.messages[row_id] = action.payload
                }
            } else {
                state.messages.push(action.payload)
                state.job_id_to_latest_message_index[job_id] = state.messages.length - 1
            }
        }
    }
})

export const { jobStatusAdded } = jobsStatusSlice.actions
export default jobsStatusSlice.reducer