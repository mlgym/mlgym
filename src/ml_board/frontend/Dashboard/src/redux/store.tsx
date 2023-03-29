import { configureStore } from '@reduxjs/toolkit';
// import { ThunkAction    } from '@reduxjs/toolkit';
// import { Action         } from '@reduxjs/toolkit';
import { evalResultCustomData } from '../worker_socket/event_handlers/evaluationResultDataHandler';
import charts from './charts/chatsSlice';
import experimentsSlice from './experiments/experimentsSlice';
import status from './status/statusSlice';
import table from './table/tableSlice';


export const store = configureStore({
  reducer: {
    status,
    experimentsSlice,
    charts,
    table
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
