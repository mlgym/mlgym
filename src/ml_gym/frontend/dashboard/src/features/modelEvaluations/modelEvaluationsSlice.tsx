import { createSlice } from '@reduxjs/toolkit'
import { ModelEvaluationMessageCollectionType, ModelEvaluationType } from '../../app/datatypes'
import type { RootState } from '../../app/store';

const initialState = {
    messages: [],
    experiment_id_to_latest_message_index: {}
} as ModelEvaluationMessageCollectionType




const modelEvaluationsSlice = createSlice({
    name: 'modelEvaluations',
    initialState,
    reducers: {
        modelEvaluationAdded(state, action) {
            state.messages.push(action.payload)
        }
    }
})

export const { modelEvaluationAdded } = modelEvaluationsSlice.actions

// export const modelEvaluationRowsSelector = (state: RootState) => state.modelsStatus.messages.map((s: ModelEvaluationType) => (
//     {
//         experiment_id: s.data.payload.experiment_id,
//         model_status: s.data.payload.status,
//         num_epochs: s.data.payload.num_epochs,
//         current_epoch: s.data.payload.current_epoch,
//         splits: s.data.payload.splits,
//         current_split: s.data.payload.current_split,
//         epoch_progress: s.data.payload.current_epoch / s.data.payload.num_epochs,
//         batch_progress: s.data.payload.current_batch / s.data.payload.num_batches,
//     } as ModelStatusRowType
// ));

export default modelEvaluationsSlice.reducer