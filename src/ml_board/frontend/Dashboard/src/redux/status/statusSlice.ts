import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

export interface StatusState {
  currentFilter: string;
  idTab: string;
  wsConnected: boolean;
  ping: number;
  received_msg_count: number;
  throughput: number;
  grid_search_id: string;
  rest_api_url: string;
}

const initialState: StatusState = {
  currentFilter: '.*',
  idTab: "analysisboard", //ASK Vijul: do we need to store the current tab? is it useful?
  wsConnected: false,
  ping: -1,
  received_msg_count: 0,
  throughput: 0,
  grid_search_id: "",
  rest_api_url: ""
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
    setSocketConnection: (state, action: PayloadAction<boolean>) => {
      state.wsConnected = action.payload
    },
    setLastPing: (state, action: PayloadAction<number>) => {
      state.ping = action.payload
    },
    incrementReceivedMsgCount: (state) => {
      state.received_msg_count++;
    },
    setThroughput: (state, { payload }: PayloadAction<number>) => {
      state.throughput = payload;
    },
    setGridSearchId: (state, action: PayloadAction<string>) => {
      state.grid_search_id = action.payload;
    },
    setRestApiUrl: (state, action: PayloadAction<string>) => {
      state.rest_api_url = action.payload;
    },
  },
  // extraReducers(builder) {
  //   builder.addCase(upsertManyRows, (state, { payload }) => {
  //     // TODO:: Loop over all and check the type, if already there add new headers, else skip
  //   })
  // },
});

export const { changeFilter, changeTab, setSocketConnection, setLastPing, incrementReceivedMsgCount, setThroughput, setGridSearchId, setRestApiUrl } = statusSlice.actions;

export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab = (state: RootState) => state.status.idTab;
export const isConnected = (state: RootState) => state.status.wsConnected;
export const getLastPing = (state: RootState) => state.status.ping;
export const getReceivevMsgCount = (state: RootState) => state.status.received_msg_count;
export const getThroughput = (state: RootState) => state.status.throughput;
export const getGridSearchId = (state: RootState) => state.status.grid_search_id;
export const getRestApiUrl = (state: RootState) => state.status.rest_api_url;

export default statusSlice.reducer;
