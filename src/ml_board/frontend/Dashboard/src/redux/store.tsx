import { configureStore } from '@reduxjs/toolkit';
// import { ThunkAction    } from '@reduxjs/toolkit';
// import { Action         } from '@reduxjs/toolkit';
import charts from './charts/chartsSlice';
import status from './status/statusSlice';
import table from './table/tableSlice';


export const store = configureStore({
  reducer: {
    status,
    charts,
    table
  }
});


export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;