import { createSlice   } from '@reduxjs/toolkit';
import { PayloadAction } from '@reduxjs/toolkit';
import { RootState     } from '../../app/store';

export interface Epoch {
  id            : number;
  [eID: string] : number;
}

export interface Experiment {
  grid_search_id : string; 
  experiment_id  : string;
  chart_ids?     : string[]; // ${split}@@${metric}
  status?        : string;
  current_split? : string;
  splits?        : string[];
  num_epochs?    : number;
  current_epoch? : number;
  num_batches?   : number;
  current_batch? : number;
  color?         : string;
  // used to keep split data -- VV    To avoid compilation error      VV
  [split_metric: string] : Epoch[] | number | string | string[] | undefined;
  // -------------------------- ^^^^^^ To avoid compilation error ^^^^^^
}

export interface ExperimentsState {
  [eID: string]: Experiment;
}

const initialState: ExperimentsState = { }

export const experimentsSlice = createSlice ({
  name: 'experiments',
  initialState,
  reducers: {
    upsertExp: (state, action: PayloadAction<Experiment>) => {
      if (state[action.payload.experiment_id] === undefined) {
        state[action.payload.experiment_id] = { ...action.payload, color: getRandColor () };
      } else {
        state[action.payload.experiment_id] = 
        mergeExperiments (state[action.payload.experiment_id], action.payload);
      }
    }
  }
});

// used so that the values in an experiment are merged rather than overwritten
// the reason this function is used is the variable object keys are not known
// e.g. "train@@F1", "val@@bceloss", or any other split@@metric identifiers
let mergeExperiments = (e1: Experiment, e2: Experiment): Experiment => {
  let res: Experiment = e1;

  // The only objects that need to be merged in type experiment are Arrays
  // only care about the already existing arrays of e1
  let entries = Object.entries (e2);
  for (let iEntry = 0; iEntry < entries.length; iEntry++) {
    let [key, val] = entries[iEntry];
    // This can only handle one-dimensional arrays
    if (Array.isArray (val)) {
      if (Array.isArray (res[key])) {
        res[key] = [ ...new Set ([ ...res[key] as Array<any>, ...e2[key]  as Array<any> ]) ];
      } else if (res[key] === undefined) {
        res[key] = e2[key];
      }
    } else if (typeof (val) === "object") { // object that isn't an array.
      // if keys with values that are objects or objects with nested objects are added
      // to the expirment a recursive function can be called here to handle them
    } else {
      // if the value is not an array
      // overwrite e1 data for that key from e2 if it exists
      res[key] = e2[key];
    }
  }

  return res;
}

// one can only hope that it doesn't produce
// a blue blue blue blue blue... pattern
const getRandColor = (): string => {
  return `#${Math.floor (Math.random () * 16777215).toString (16)}`;
}

export const { upsertExp } = experimentsSlice.actions;
export const selectExperiments = (state: RootState) => state.experiments;
export const selectExperiment  = (state: RootState, target: string) => state.experiments[target];
export default experimentsSlice.reducer;