// import { createEntityAdapter, createSlice, EntityState } from "@reduxjs/toolkit";
// import { RootState } from "../store";

// export interface Experiment {
//     experiment_id: number;
//     model_status: string;   // <TRAINING, EVALUATING>,
//     current_split: string;
//     splits: string[]; //e.g.: ["train", "val", "test"],
//     num_epochs: number;
//     current_epoch: number;
//     num_batches: number;
//     current_batch: number;
//     // this is the lastest metric value per split (number, the rest is to avoid compilation error)
//     [latest_split_metric: string]: number | string | string[];
// }

// const experimentsAdapter = createEntityAdapter<Experiment>({
//     selectId: ({ experiment_id }: Experiment) => experiment_id,
//     // sortComparer: ({ experiment_id: id1 }: Experiment, { experiment_id: id2 }: Experiment) => id1.localeCompare(id2),
// });

// // interface ExperimentsState {
// //     // The unique IDs of each experiment.
// //     ids: [];
// //     // A lookup table mapping experiment IDs to the corresponding Experiment objects
// //     entities: {};
// // }

// const initialState: EntityState<Experiment> = experimentsAdapter.getInitialState({});

// export const experimentsSlice = createSlice({
//     name: 'experiments',
//     initialState,
//     reducers: {
//         // TODO: Override to add the latest_split_metric
//         upsertExperiment: experimentsAdapter.upsertOne, //(state, action.payload);
//         // upsertExperiment:(state, action: PayloadAction<Experiment>) => {
//         // const { experiment_id } = action.payload;
//         // const experiment = state.entities[experiment_id];
//         // if (experiment === undefined) {
//         //   experimentAdapter.addOne(state, action.payload);
//         // } else {
//         //   experimentAdapter.updateOne(state,)
//         //   mergeExperiments(experiment, action.payload);
//         // }
//         // if (state[action.payload.experiment_id] === undefined) {
//         //   state[action.payload.experiment_id] = { ...action.payload, color: getRandColor() };
//         // } else {
//         //   state[action.payload.experiment_id] =
//         //     mergeExperiments(state[action.payload.experiment_id], action.payload);
//         // }
//         // }
//         updateExperiment: experimentsAdapter.updateOne,
//     }
// });


// export const { upsertExperiment, updateExperiment } = experimentsSlice.actions;

// // create a set of memoized selectors
// export const {
//     selectById: selectExperimentById,
//     selectEntities: selectExperiments,
// } = experimentsAdapter.getSelectors((state: RootState) => state.experiments)

// export default experimentsSlice.reducer;
export { };
