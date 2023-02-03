// ASK: VIJUL BEFORE ANY TODO HERE?!
import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '../store';

const initialState = {
    // ASK Vijul: no need for this indentation "evalResult"?
    evalResult: {
        // TODO: move this outside to the status slice for example? (ASK MAX)
        grid_search_id: null,
        experiments: {},
        // TODO: move this outside to the status slice
        colors_mapped_to_exp_id: [[],[]]
    }
}

// ASK Vijul: rame name this to charts?
const experimentsSlice = createSlice({
    name: "experimentsSlice",
    initialState: initialState,
    reducers: {
        saveEvalResultData: (state, param) => {
            state.evalResult = param.payload
        }
    }
});

export const selectEvalResult = (state: RootState) => state.experimentsSlice.evalResult

const { actions, reducer } = experimentsSlice
export const { saveEvalResultData } = actions;
export default reducer;