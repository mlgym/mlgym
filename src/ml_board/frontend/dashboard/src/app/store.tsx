import { configureStore, ThunkAction, Action, } from '@reduxjs/toolkit'
import jobStatusReducer from '../features/jobsStatus/jobsStatusSlice'
import modelStatusReducer from '../features/modelsStatus/modelsStatusSlice'
import modelEvaluationReducer from '../features/modelEvaluations/modelEvaluationsSlice'
import experimentConfigReducer from '../features/experimentConfig/experimentConfigSlice';


export const store = configureStore({
  reducer: {
    jobsStatus: jobStatusReducer,
    modelsStatus: modelStatusReducer,
    modelsEvaluation: modelEvaluationReducer,
    experimentConfig: experimentConfigReducer
  }
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<ReturnType, RootState, unknown, Action<string>>;
