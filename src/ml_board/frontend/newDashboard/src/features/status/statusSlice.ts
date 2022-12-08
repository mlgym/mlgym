import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export interface StatusState {
  currentFilter : string;
  iTab          : number;
  wsConnected   : boolean;
  lastPing?     : number;
  lastPong?     : number;
}

const initialState: StatusState = {
  currentFilter : '.*',
  iTab          : 0,
  wsConnected   : false
};

export const statusSlice = createSlice ({
  name: 'status',
  initialState,
  reducers: {
    changeFilter: (state, action: PayloadAction<string>) => {
      state.currentFilter = action.payload;
    },
    changeTab: (state, action: PayloadAction<number>) => {
      state.iTab = action.payload;
    },
    changeSocket: (state, action: PayloadAction<boolean>) => {
      state.wsConnected = action.payload
    },
    setLastPing: (state, action: PayloadAction<number>) => {
      state.lastPing = action.payload
    },
    setLastPong: (state, action: PayloadAction<number>) => {
      state.lastPong = action.payload
    }
  }
});

export const { changeFilter, changeTab, changeSocket, setLastPing, setLastPong } = statusSlice.actions;
export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab    = (state: RootState) => state.status.iTab;
export const isConnected  = (state: RootState) => state.status.wsConnected;
export const getLastPing  = (state: RootState) => state.status.lastPing;
export const getLastPong  = (state: RootState) => state.status.lastPong;
export default statusSlice.reducer;
