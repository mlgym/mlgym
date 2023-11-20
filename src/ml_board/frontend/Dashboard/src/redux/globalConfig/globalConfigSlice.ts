import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

interface GlobalConfig {
  currentFilter: string;
  idTab: string;
  wsConnected: boolean;
  ping: number;
  received_msg_count: number;
  throughput: number;
  grid_search_id: string;
  rest_api_url: string;
  socket_connection_url: string;
}

const initialState: GlobalConfig = {
  currentFilter: '.*',
  idTab: "analysisboard",
  wsConnected: false,
  ping: -1,
  received_msg_count: 0,
  throughput: 0,
  grid_search_id: "",
  rest_api_url: "",
  socket_connection_url: ""
};

const { actions, reducer } = createSlice({
  name: 'GlobalConfig',
  initialState,
  reducers: {
    setFilter: (state, { payload }: PayloadAction<string>) => {
      state.currentFilter = payload;
    },
    changeTab: (state, { payload }: PayloadAction<string>) => {
      state.idTab = payload;
    },
    setSocketConnection: (state, { payload }: PayloadAction<boolean>) => {
      state.wsConnected = payload
    },
    setLastPing: (state, { payload }: PayloadAction<number>) => {
      state.ping = payload
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
    setSocketConnectionUrl: (state, action: PayloadAction<string>) => {
      state.socket_connection_url = action.payload;
    },
  },
  // extraReducers(builder) {
  //   builder.addCase(upsertManyRows, (state, { payload }) => {
  //     // TODO:: Loop over all and check the type, if already there add new headers, else skip
  //   })
  // },
});

export const { setFilter, changeTab, setSocketConnection, setLastPing, incrementReceivedMsgCount, setThroughput, setGridSearchId, setRestApiUrl, setSocketConnectionUrl } = actions;

export const selectFilter = (state: RootState) => state.globalConfig.currentFilter;
export const selectTab = (state: RootState) => state.globalConfig.idTab;
export const isConnected = (state: RootState) => state.globalConfig.wsConnected;
export const getLastPing = (state: RootState) => state.globalConfig.ping;
export const getReceivevMsgCount = (state: RootState) => state.globalConfig.received_msg_count;
export const getThroughput = (state: RootState) => state.globalConfig.throughput;
export const getGridSearchId = (state: RootState) => state.globalConfig.grid_search_id;
export const getRestApiUrl = (state: RootState) => state.globalConfig.rest_api_url;
export const getSocketConnectionUrl = (state: RootState) => state.globalConfig.socket_connection_url;

export default reducer;
