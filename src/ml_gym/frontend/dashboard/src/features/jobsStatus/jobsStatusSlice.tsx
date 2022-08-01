import { createSlice } from '@reduxjs/toolkit'
import { JobStatusMessageCollectionType, JobStatusType, JobStatusRowType} from '../../app/datatypes'
import type { RootState } from '../../app/store';



const initialState = {
    messages: [],
    job_id_to_latest_message_index: {}
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

export const jobStatusRowsSelector = (state: RootState) => state.jobsStatus.messages.map((s: JobStatusType) => (
    {
        job_id: s.data.payload.job_id,
        job_type: s.data.payload.job_type,
        job_status: s.data.payload.status,
        experiment_id: s.data.payload.experiment_id,
        starting_time: s.data.payload.starting_time,
        finishing_time: s.data.payload.finishing_time,
        error: s.data.payload.error,
        stacktrace: s.data.payload.stacktrace,
        device: s.data.payload.device,
    } as JobStatusRowType
));


export default jobsStatusSlice.reducer
