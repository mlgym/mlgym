import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

// TODO: ASK MAX, renaming to GlobalConfigSlice
export interface StatusState {
  currentFilter: string;
  idTab: string;
  wsConnected: boolean;
  ping: number;
  received_msg_count: number;
  throughput: number;
  grid_search_id: string;
  metric_loss: Array<string>;
  rest_api_url: string;
  socket_connection_url: string;
}

const initialState: StatusState = {
  currentFilter: '.*',
  idTab: "Dashboard", //TODO: redundant??
  wsConnected: false,
  ping: -1,
  received_msg_count: 0,
  throughput: 0,
  grid_search_id: "",
  metric_loss: [], //TODO: redundant??
  rest_api_url: "",
  socket_connection_url: ""
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
    setSocketConnectionUrl: (state, action: PayloadAction<string>) => {
      state.socket_connection_url = action.payload;
    },
    // ASK MAX: To be used if we want to save the Metric or Losses key here for the table
    // I stopped from doing so because then function is going to be called every evaluation_result message!!!
    upsertMetricOrLoss: (state, { payload }: PayloadAction<string[]>) => {
      state.metric_loss.push(...payload);
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

export const { changeFilter, changeTab, setSocketConnection, setLastPing, incrementReceivedMsgCount, setThroughput, setGridSearchId, setRestApiUrl, setSocketConnectionUrl } = statusSlice.actions;

export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab = (state: RootState) => state.status.idTab;
export const isConnected = (state: RootState) => state.status.wsConnected;
export const getLastPing = (state: RootState) => state.status.ping;
export const getReceivevMsgCount = (state: RootState) => state.status.received_msg_count;
export const getThroughput = (state: RootState) => state.status.throughput;
export const getGridSearchId = (state: RootState) => state.status.grid_search_id;
export const getRestApiUrl = (state: RootState) => state.status.rest_api_url;
export const getSocketConnectionUrl = (state: RootState) => state.status.socket_connection_url;

export default statusSlice.reducer;
