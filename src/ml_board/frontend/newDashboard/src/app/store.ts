import { configureStore } from '@reduxjs/toolkit';
import { ThunkAction    } from '@reduxjs/toolkit';
import { Action         } from '@reduxjs/toolkit';
import experiments        from '../features/experiments/experimentsSlice';
import jobs               from '../features/jobs/jobsSlice';
import status             from '../features/status/statusSlice';
import ExperimentsReducer from '../redux/reducers/ExperimentsReducer';

export const store = configureStore ({
  reducer: {
    experiments,
    jobs,
    status,
    ExperimentsReducer
  }
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
