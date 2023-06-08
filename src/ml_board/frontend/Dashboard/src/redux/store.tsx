import { configureStore } from '@reduxjs/toolkit';
// import { ThunkAction    } from '@reduxjs/toolkit';
// import { Action         } from '@reduxjs/toolkit';
import charts from './charts/chartsSlice';
import globalConfig from './globalConfig/globalConfigSlice';
import table from './table/tableSlice';


export const store = configureStore({
  reducer: {
    globalConfig,
    charts,
    table
  }
});


export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;