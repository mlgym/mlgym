import { configureStore } from '@reduxjs/toolkit';
import { ThunkAction    } from '@reduxjs/toolkit';
import { Action         } from '@reduxjs/toolkit';
import status             from './status/statusSlice';
import experimentsSlice from './experiments/experimentsSlice';
import { evalResultCustomData } from '../webworkers/event_handlers/evaluationResultDataHandler';

export const store = configureStore ({
  reducer: {
    status,
    experimentsSlice,
  }
});

export type reduxState = {
  experimentsSlice: {
    evalResult: evalResultCustomData
  }
}
export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
