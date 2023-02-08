import { configureStore } from '@reduxjs/toolkit';
// import { ThunkAction    } from '@reduxjs/toolkit';
// import { Action         } from '@reduxjs/toolkit';
import { evalResultCustomData } from '../webworkers/event_handlers/evaluationResultDataHandler';
import charts from './charts/chatsSlice';
import experimentsSlice from './experiments/experimentsSlice';
import experiments from './experiments/yetAnotherExperimentSlice';
import jobs from './jobs/jobSlice';
import status from './status/statusSlice';


export const store = configureStore({
  reducer: {
    status,
    experimentsSlice,
    jobs,
    experiments,
    charts,
  }
});

export type reduxState = {
  experimentsSlice: {
    evalResult: evalResultCustomData
  }
}
export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
// export type AppThunk<ReturnType = void> = ThunkAction<
//   ReturnType,
//   RootState,
//   unknown,
//   Action<string>
// >;
