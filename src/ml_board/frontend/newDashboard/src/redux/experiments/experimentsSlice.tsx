import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    evalResult: {
        grid_search_id: null,
        experiments: {},
        colors_mapped_to_exp_id: [[],[]]
    }
}

const experimentsSlice = createSlice({
    name: "experimentsSlice",
    initialState: initialState,
    reducers: {
        saveEvalResultData: (state, param) => {
            state.evalResult = param.payload
        }
    }
});

const { actions, reducer } = experimentsSlice
export const { saveEvalResultData } = actions;
export default reducer;