import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

export interface StatusState {
  currentFilter : string;
  iTab          : number;
}

const initialState: StatusState = {
  currentFilter : '.*',
  iTab          : 0
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
    }
  }
});

export const { changeFilter, changeTab } = statusSlice.actions;
export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab    = (state: RootState) => state.status.iTab;
export default statusSlice.reducer;
