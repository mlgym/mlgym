import { createSlice } from '@reduxjs/toolkit'
import { ExperimentConfigMessageCollectionType, ExperimentConfigType} from '../../app/datatypes'
import type { RootState } from '../../app/store';

const initialState = {
    messages: [],
    experiment_id_to_message_index: {}
} as ExperimentConfigMessageCollectionType


const experimentConfigSlice = createSlice({
    name: 'experimentConfig',
    initialState,
    reducers: {
        experimentConfigAdded(state, action) {
            const experiment_id: number = action.payload.data.payload.experiment_id
            if (experiment_id in state.experiment_id_to_message_index) {
                const row_id = state.experiment_id_to_message_index[experiment_id]
                // prevents possible race condition
                if (state.messages[row_id].event_id < action.payload.event_id) {
                    state.messages[row_id] = action.payload
                }
            } else {
                state.messages.push(action.payload)
                state.experiment_id_to_message_index[experiment_id] = state.messages.length - 1
            }
        }
    }
})

export const { experimentConfigAdded } = experimentConfigSlice.actions

// export const experimentConfigRowsSelector = (state: RootState) => state.experimentConfig.messages.map((s: ExperimentConfigType) => (
//     {
//         experiment_id: s.data.payload.experiment_id,
//         grid_search_id: s.data.payload.grid_search_id,
//         job_id: s.data.payload.job_id,
//         config: s.data.payload.config,
//     } as ExperimentConfigRowType
// ));

export default experimentConfigSlice.reducer
