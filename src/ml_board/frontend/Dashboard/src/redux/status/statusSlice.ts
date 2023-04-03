import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { upsertCharts } from '../charts/chartsSlice';
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
  color_map: { [expID: string]: string }; // expID mapped to a color
  metric_loss: Array<string>;
}

const initialState: StatusState = {
  currentFilter: '.*',
  idTab: "Dashboard", //TODO: redundant??
  wsConnected: false,
  ping: -1,
  received_msg_count: 0,
  throughput: 0,
  grid_search_id: "",
  color_map: {},
  metric_loss: [] //TODO: redundant??
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
    // ASK MAX: To be used if we want to save the Metric or Losses key here for the table
    // I stopped from doing so because then function is going to be called every evaluation_result message!!!
    upsertMetricOrLoss: (state, { payload }: PayloadAction<string[]>) => {
      state.metric_loss.push(...payload);
    }
  }, extraReducers(builder) {
    builder.addCase(upsertCharts, (state, { payload }) => {
      if (!state.color_map.hasOwnProperty(payload[0].exp_id)) {
        // one can only hope that it doesn't produce a blue blue blue blue blue... pattern :')
        state.color_map[payload[0].exp_id] = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
      }
    })
  },
});

export const { changeFilter, changeTab, setSocketConnection, setLastPing, incrementReceivedMsgCount, setThroughput } = statusSlice.actions;
export const selectFilter = (state: RootState) => state.status.currentFilter;
export const selectTab = (state: RootState) => state.status.idTab;
export const isConnected = (state: RootState) => state.status.wsConnected;
export const getLastPing = (state: RootState) => state.status.ping;
export const getReceivevMsgCount = (state: RootState) => state.status.received_msg_count;
export const getThroughput = (state: RootState) => state.status.throughput;
export const selectColorMap = (state: RootState) => state.status.color_map;
export default statusSlice.reducer;
