import { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import Template from './template/template';
import FlowBoard from './routes/flow_board'
import AnalysisBoard from './routes/analysis_board'
import Settings from './routes/settings'
import Throughput from './routes/throughput_board'
import io from 'socket.io-client';
import { BrowserRouter, Route, Routes, useSearchParams } from 'react-router-dom';
import { useAppDispatch } from "./app/hooks"
import { IOStatsType, FilterConfigType } from "./app/datatypes"
import { jobStatusAdded } from "./features/jobsStatus/jobsStatusSlice"
import { modelStatusAdded } from "./features/modelsStatus/modelsStatusSlice"
import { experimentConfigAdded } from "./features/experimentConfig/experimentConfigSlice"
import { modelEvaluationAdded } from "./features/modelEvaluations/modelEvaluationsSlice"
import { AlertMessage } from "./features/alertMessage/alertMessage"
import 'bootstrap/dist/css/bootstrap.min.css';



export type AlertMessageType = {
  alertId: number
  heading: string;
  message: string;
  invalid: boolean;
};

export type CmdSettingsType = {
  wsEndpoint: string;
  restEndpoint: string;
  runId: string;
};

export default function App() {

  const [alertMessages, setAlertMessages] = useState<Array<AlertMessageType>>([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const [cmdSettings, setcmdSettings] = useState<CmdSettingsType>({ "wsEndpoint": "", "restEndpoint": "", "runId": "" });
  const [sideBarExpanded, setSideBarExpanded] = useState<boolean>(false);
  const [selectedPageId, setSelectedPageId] = useState<number>(0)
  const [ioStats, setIOStats] = useState<IOStatsType>({ isConnected: false, msgTS: [], lastPing: 0, lastPong: 0 });

  const [filterConfig, setFilterConfig] = useState<FilterConfigType>({ metricFilterRegex: ".*", tmpMetricFilterRegex: ".*" })

  const appDispatch = useAppDispatch()


  // ============ IOSTATS functions ============
  const setLastPing = (ts: number) => {
    setIOStats(oldIOStats => ({
      ...oldIOStats,
      msgTS: [...oldIOStats["msgTS"]],
      lastPing: ts
    }))
  }

  const setLastPong = (ts: number) => {
    setIOStats(oldIOStats => ({
      ...oldIOStats,
      msgTS: [...oldIOStats["msgTS"]],
      lastPong: ts
    }))
  }

  const setIsConnected = (val: boolean) => {
    setIOStats(oldIOStats => ({
      ...oldIOStats,
      msgTS: [...oldIOStats["msgTS"]],
      isConnected: val
    }))
  }

  const addMsgTs = (ts: number) => {
    setIOStats(oldIOStats => ({
      ...oldIOStats,
      msgTS: [...oldIOStats["msgTS"], ts],
    }))
  }

  // ============ MLgym Messages functions ============

  const eventTypeToActionCreator: any = {
    "job_status": jobStatusAdded,
    "experiment_status": modelStatusAdded,
    "evaluation_result": modelEvaluationAdded,
    "experiment_config": experimentConfigAdded
  }

  useEffect(() => { // setting state within useEffect: https://stackoverflow.com/questions/53715465/can-i-set-state-inside-a-useeffect-hook
    if (searchParams.has("rest_endpoint") && searchParams.has("ws_endpoint")) {
      const restEndpoint = searchParams.get("rest_endpoint")
      const wsEndpoint = searchParams.get("ws_endpoint")
      const runId = searchParams.get("run_id")
      if (restEndpoint !== null && wsEndpoint !== null && runId !== null) {
        const c: CmdSettingsType = { "wsEndpoint": wsEndpoint, "restEndpoint": restEndpoint, "runId": runId }
        setcmdSettings(() => c)
        console.log("connecting to ... " + wsEndpoint)
        const socket = io(wsEndpoint);

        socket.on('connect', () => {
          setIsConnected(true);
          socket.emit('join', { rooms: [runId] });
        });

        socket.on('disconnect', () => {
          setIsConnected(false);
        });

        socket.on('connect_error', function (err) {
          // handle server error here
          console.log('Error connecting to server');
          const message = "Cannot conntect to " + wsEndpoint + " ... " + err
          addAlertMessage("Websocket Error", message)
        });

        socket.on('mlgym_event', (msg) => {
          addMsgTs(new Date().getTime())
          const msgRep = msg // JSON.parse(msg)
          const eventType: string = msgRep["data"]["event_type"]
          if (eventType in eventTypeToActionCreator) {
            const actionCreator = eventTypeToActionCreator[eventType]
            appDispatch(actionCreator(msgRep))
          } else {
            console.log("WARNING: eventy type " + eventType + " not supported!")
          }
        });

        socket.on('pong', () => {
          setLastPong(new Date().getTime())
        });

        const interval = setInterval(() => {
          setLastPing(new Date().getTime())
          socket.emit('ping');
        }, 1000);

        return () => {
          socket.off('connect');
          socket.off('disconnect');
          socket.off('mlgym_event');
          socket.off('pong');
          clearInterval(interval);
        };
      }
    }
    addAlertMessage("Initial search params insufficient", "Please use the URL provided via the command line to access MLboard. The URL provides the endpoints and run id via the query parameters.")
  }, []);



  const toggleSideBar = () => {
    setSideBarExpanded(!sideBarExpanded);
  };



  // const msgs_rep = msgs.map(m => (<div> {JSON.stringify(m)}</div>))

  const removeAlertMessage = (alertId: number) => {
    const updatedAlertMessages = [...alertMessages];
    updatedAlertMessages[alertId].invalid = true
    setAlertMessages(updatedAlertMessages)
  };

  const addAlertMessage = (heading: string, message: string) => {
    // setting state within useEffect: https://stackoverflow.com/questions/53715465/can-i-set-state-inside-a-useeffect-hook
    setAlertMessages(alertMessages => [...alertMessages, { "alertId": alertMessages.length, "heading": heading, "message": message, "invalid": false }])
  }


  const alertMessageComponents = alertMessages.filter(alertMessage => !alertMessage.invalid).map((alertMessage) => <AlertMessage
    alertId={alertMessage.alertId}
    heading={alertMessage.heading}
    message={alertMessage.message}
    removeAlertMessage={() => removeAlertMessage(alertMessage.alertId)} />
  );

  return (
    <div className="App">
      {
        alertMessageComponents
      }
      <Template toggleSidebar={toggleSideBar}
        sideBarExpanded={sideBarExpanded}
        setSelectedPageId={setSelectedPageId}
        selectedPageId={selectedPageId}
        filterConfig={filterConfig}
        setFilterConfig={setFilterConfig}
      >

        <Routes>
          <Route
            path="/flowboard"
            element={<FlowBoard />}
          />
          <Route
            path="/analysisboard"
            element={<AnalysisBoard filterConfig={filterConfig} />}
          />
          <Route
            path="/throughput"
            element={<Throughput ioStats={ioStats} />}
          />
          <Route
            path="/settings"
            element={<Settings />}
          />

        </Routes>
      </Template>
    </div>);
}