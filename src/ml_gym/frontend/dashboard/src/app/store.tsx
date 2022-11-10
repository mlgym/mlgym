import { Action, configureStore, ThunkAction } from '@reduxjs/toolkit';
import experimentConfigReducer from '../features/experimentConfig/experimentConfigSlice';
import RegExReducer from '../features/globalConfig/RegExSlice';
import jobStatusReducer from '../features/jobsStatus/jobsStatusSlice';
import modelEvaluationReducer from '../features/modelEvaluations/modelEvaluationsSlice';
import modelStatusReducer from '../features/modelsStatus/modelsStatusSlice';


export const store = configureStore({
  reducer: {
    jobsStatus: jobStatusReducer,
    modelsStatus: modelStatusReducer,
    modelsEvaluation: modelEvaluationReducer,
    experimentConfig: experimentConfigReducer,
    RegEx : RegExReducer
  }
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<ReturnType, RootState, unknown, Action<string>>;
