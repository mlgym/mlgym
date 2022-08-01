import { configureStore, ThunkAction, Action, } from '@reduxjs/toolkit'
import jobStatusReducer from '../features/jobsStatus/jobsStatusSlice'
import modelStatusReducer from '../features/modelsStatus/modelsStatusSlice'


export const store = configureStore({
  reducer: {
    jobsStatus: jobStatusReducer,
    modelsStatus: modelStatusReducer
  }
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<ReturnType, RootState, unknown, Action<string>>;
