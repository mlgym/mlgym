import { configureStore } from '@reduxjs/toolkit';
import { ThunkAction    } from '@reduxjs/toolkit';
import { Action         } from '@reduxjs/toolkit';
import status             from './status/statusSlice';
import experimentsSlice from './experiments/experimentsSlice';

export const store = configureStore ({
  reducer: {
    status,
    experimentsSlice,
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
