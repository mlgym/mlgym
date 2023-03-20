// import { createSlice } from '@reduxjs/toolkit';
// import { RootState } from '../store';

// const initialState = {
//     // TODO Vijul: no need for this indentation layer "evalResult"?
//     evalResult: {
//         // TODO: move this outside to the status slice for example? (ASK MAX)
//         grid_search_id: null,
//         experiments: {},
//         // TODO: move this outside to the status slice
//         colors_mapped_to_exp_id: [[], []]
//     }
// }

// // const initialState = {
// //     experiments: {},
// //     // TODO: move this outside to the status slice
// //     colors_mapped_to_exp_id: [[], []]
// // }


// // TODO Vijul: Renameing this to charts and the whole file too???
// // const chartsSlice = createSlice({
// const experimentsSlice = createSlice({
//     // name: "charts",
//     name: "experimentsSlice",
//     initialState: initialState,
//     reducers: {
//         saveEvalResultData: (state, param) => {
//             // note that inside the slice reducer the "state" is NOT the "RootState", it's only the sliced state
//             // state = param.payload
//             state.evalResult = param.payload
//         }
//     }
// });

// // export const selectEvalResult = (state: RootState) => state.charts
// export const selectEvalResult = (state: RootState) => state.experimentsSlice.evalResult

// const { actions, reducer } = experimentsSlice
// export const { saveEvalResultData } = actions;
// export default reducer;

export { };

// NOTE: if Experiments were to get their own Slice!
// interface ExperimentsSlice {
//     // The unique IDs of each Row.
//     ids: [exp_id, ...];
//     // A lookup table mapping Rows' IDs to the corresponding Row objects
//     entities: {
//         [exp_id]:{
//             exp_id,
//             chart:{
//                 [chart_id]: Array<number>
//             }
//         }
//     };
// }