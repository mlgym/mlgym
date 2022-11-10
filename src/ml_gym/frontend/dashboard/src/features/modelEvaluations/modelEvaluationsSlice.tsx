import { createSlice } from '@reduxjs/toolkit';
import { ModelEvaluationMessageCollectionType } from '../../app/datatypes';

const initialState = {
    messages: [],
    experiment_id_to_latest_message_index: {}
} as ModelEvaluationMessageCollectionType




const modelEvaluationsSlice = createSlice({
    name: 'modelEvaluations',
    initialState,
    reducers: {
        modelEvaluationAdded(state, action) {
            const experiment_id: number = action.payload.data.payload.experiment_id
            if (experiment_id in state.experiment_id_to_latest_message_index) {
                const row_id = state.experiment_id_to_latest_message_index[experiment_id]
                // prevents possible race condition
                if (state.messages[row_id].event_id < action.payload.event_id) {
                    state.messages[row_id] = action.payload
                }
            } else {
                state.messages.push(action.payload)
                state.experiment_id_to_latest_message_index[experiment_id] = state.messages.length - 1
            }
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

// export const metricStatusRowsSelector = (state: RootState) =>
//     state.modelsEvaluation.messages.map((element) => element.data.payload.metric_scores);

export default modelEvaluationsSlice.reducer