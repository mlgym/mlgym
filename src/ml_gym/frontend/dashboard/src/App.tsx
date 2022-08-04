import { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import Template from './template/template';
import FlowBoard from './routes/flow_board'
import AnalysisBoard from './routes/analysis_board'
import Settings from './routes/settings'
import Throughput from './routes/throughput_board'
import io from 'socket.io-client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useAppDispatch } from "./app/hooks"
import { IOStatsType, FilterConfigType } from "./app/datatypes"
import { jobStatusAdded } from "./features/jobsStatus/jobsStatusSlice"
import { modelStatusAdded } from "./features/modelsStatus/modelsStatusSlice"
import { modelEvaluationAdded } from "./features/modelEvaluations/modelEvaluationsSlice"
import 'bootstrap/dist/css/bootstrap.min.css';


const socket = io("http://localhost:7000");


export default function App() {

  const [sideBarExpanded, setSideBarExpanded] = useState<boolean>(false);
  const [selectedPageId, setSelectedPageId] = useState<number>(0)
  const [ioStats, setIOStats] = useState<IOStatsType>({ isConnected: socket.connected, msgTS: [], lastPing: 0, lastPong: 0 });

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
    // "experiment_status": modelStatusAdded,
    "evaluation_result": modelEvaluationAdded
  }

  useEffect(() => {

    socket.on('connect', () => {
      setIsConnected(true);
      socket.emit('join', { rooms: ['mlgym_event_subscribers'] });
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('mlgym_event', (msg) => {
      addMsgTs(new Date().getTime())
      const msgRep = JSON.parse(msg)
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
  }, []);



  const toggleSideBar = () => {
    setSideBarExpanded(!sideBarExpanded);
  };



  // const msgs_rep = msgs.map(m => (<div> {JSON.stringify(m)}</div>))


  return (
    <BrowserRouter>
      <div className="App">
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
              element={<AnalysisBoard filterConfig={filterConfig}/>}
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
      </div>
    </BrowserRouter>);
}