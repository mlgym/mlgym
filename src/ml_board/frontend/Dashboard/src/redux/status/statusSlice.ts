import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

export interface StatusState {
  currentFilter: string;
  idTab: string;
  wsConnected: boolean;
  lastPing?     : number;
  lastPong?     : number;
  grid_search_id?: string;
  color_map: { [expID: string]: string }; // expID mapped to a color
}

const initialState: StatusState = {
  currentFilter: '.*',
  idTab: "Dashboard",
  wsConnected: false,
  color_map: {},
};

export const statusSlice = createSlice({
  name: 'status',
  initialState,
  reducers: {
    changeFilter: (state, action: PayloadAction<string>) => {
      state.currentFilter = action.payload;
    },
    changeTab: (state, { payload }: PayloadAction<string>) => {
      state.idTab = payload;
    },
    changeSocketConnection: (state, action: PayloadAction<boolean>) => {
      state.wsConnected = action.payload
    },
    setLastPing: (state, action: PayloadAction<number>) => {
      state.lastPing = action.payload
    },
    setLastPong: (state, action: PayloadAction<number>) => {
      state.lastPong = action.payload
    },
    setGridSearchId: (state, action: PayloadAction<string>) => {
      state.grid_search_id = action.payload;
    },
  }
});

export const { changeFilter, changeTab, changeSocketConnection, setLastPing, setLastPong } = statusSlice.actions;
export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab = (state: RootState) => state.status.idTab;
export const isConnected  = (state: RootState) => state.status.wsConnected;
export const getLastPing  = (state: RootState) => state.status.lastPing;
export const getLastPong  = (state: RootState) => state.status.lastPong;
export const selectColorMap = (state: RootState) => state.status.color_map;
export default statusSlice.reducer;
