import { configureStore, ThunkAction, Action, } from '@reduxjs/toolkit'
import jobStatusReducer from '../features/jobsStatus/jobsStatusSlice'
import pingReducer from '../features/ping/pingSlice'

export const store = configureStore({
  reducer: {
    jobStatus: jobStatusReducer,
    ping: pingReducer
  }
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<ReturnType, RootState, unknown, Action<string>>;
