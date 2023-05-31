import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

export interface GlobalConfig {
  currentFilter: string;
  idTab: string;
  wsConnected: boolean;
  ping: number;
  received_msg_count: number;
  throughput: number;
  grid_search_id: string;
  table_headers: Array<string>;
  rest_api_url: string;
}

const initialState: GlobalConfig = {
  currentFilter: '.*',
  idTab: "analysisboard", //ASK Vijul: do we need to store the current tab? is it useful?
  wsConnected: false,
  ping: -1,
  received_msg_count: 0,
  throughput: 0,
  grid_search_id: "",
  table_headers: [], //TODO: will be used to store the ALL column headers
  rest_api_url: ""
};

export const globalConfigSlice = createSlice({
  name: 'GlobalConfig',
  initialState,
  reducers: {
    changeFilter: (state, { payload }: PayloadAction<string>) => {
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
    // TODO::
    upsertTableHeaders: (state, { payload }: PayloadAction<string[]>) => {
      state.table_headers.push(...payload);
    }
  }, 
  // extraReducers(builder) {
  //   builder.addCase(upsertCharts, (state, { payload }) => {
  //     // NOTE: very important to notice here that +4 increment
  //     // because in the testing file every evaluation_result held 4 values for the same experiment
  //     // this might not be true with other data
  //     for (let i = 0; i < payload.length; i+=4) {
  //       if (!state.color_map.hasOwnProperty(payload[i].exp_id)) {
  //         // one can only hope that it doesn't produce a blue blue blue blue blue... pattern :')
  //         state.color_map[payload[i].exp_id] = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
  //       }
  //     }
  //   })
  // },
});

export const { changeFilter, changeTab, setSocketConnection, setLastPing, incrementReceivedMsgCount, setThroughput, setGridSearchId, setRestApiUrl } = globalConfigSlice.actions;

export const selectFilter = (state: RootState) => state.globalConfig.currentFilter;
export const selectTab = (state: RootState) => state.globalConfig.idTab;
export const isConnected = (state: RootState) => state.globalConfig.wsConnected;
export const getLastPing = (state: RootState) => state.globalConfig.ping;
export const getReceivevMsgCount = (state: RootState) => state.globalConfig.received_msg_count;
export const getThroughput = (state: RootState) => state.globalConfig.throughput;
export const getGridSearchId = (state: RootState) => state.globalConfig.grid_search_id;
export const getRestApiUrl = (state: RootState) => state.globalConfig.rest_api_url;

export default globalConfigSlice.reducer;
