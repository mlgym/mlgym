// external deps
import { Route           } from 'react-router-dom';
import { Routes          } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';
import { Socket          } from 'socket.io-client';
import io                  from 'socket.io-client';

// internal deps
// import Alerts              from './ui/alerts/Alerts';
import Filter              from './ui/filter/Filter';
import Chartboard          from './ui/routes/Chartboard';
import Dashboard           from './ui/routes/Dashboard';
import Settings            from './ui/routes/Settings';
import Throughput          from './ui/routes/Throughput';
import Tabs                from './ui/tabs/Tabs';

// styles
import './App.scss';

// state-selectors
import { useAppSelector } from './app/hooks';
import { getLastPing    } from './features/status/statusSlice';
import { getLastPong    } from './features/status/statusSlice';
import { isConnected    } from './features/status/statusSlice';

// actions
import { useAppDispatch    } from './app/hooks';
import { setLastPing       } from './features/status/statusSlice';
import { setLastPong       } from './features/status/statusSlice';
import { changeSocket      } from './features/status/statusSlice';
import { convertJob        } from './features/jobs/jobsAPI';
import { serverJob         } from './features/jobs/jobsAPI';
import { convertExperiment } from './features/experiments/experimentsAPI';
import { serverExpriment   } from './features/experiments/experimentsAPI';
import { Experiment        } from './features/experiments/experimentsSlice';
import { upsertExp         } from './features/experiments/experimentsSlice';
import { Job               } from './features/jobs/jobsSlice';
import { upsertJob         } from './features/jobs/jobsSlice';
import { AppDispatch       } from './app/store';

import AppNew from './app/AppNew';

// globals - can be put in the state if you plan to presist your state
// otherwise it doesn't matter, since on refresh everything resets.
let supportedEvents = [
  "job_status",
  "job_scheduled",
  "experiment_status",
  "experiment_config",
  "evaluation_result"
];

type supportedEvents = "job_status" | "job_scheduled" | "evaluation_result"
                     | "experiment_status" | "experiment_config"
                     | "unknown"; // used for defaulting when varifying an mlgym msg

let interval: NodeJS.Timer | undefined = undefined;
let lastPing: number | undefined = undefined;
let lastPong: number | undefined = undefined;
let searchParams: URLSearchParams | undefined = undefined;
let socket: Socket<any, any>;
let joinedRoom: boolean = false;

function App() {
  lastPing = useAppSelector (getLastPing);
  lastPong = useAppSelector (getLastPong);
  [searchParams] = useSearchParams ();
  let dispatch   = useAppDispatch  ();
  let runId = searchParams.get ("run_id") || "mlgym_event_subscribers";

  if (!useAppSelector (isConnected)) {
    // wsConnect ("http://localhost:7000", runId, dispatch);
  } else {
    if (!joinedRoom) {
      socket.emit ('join', { rooms: [runId], client_id: "3000" });
      joinedRoom = true;
    }
  }

  return (
    <div className="App">
      {/* {Alerts ()} */}

      {Tabs   ()}
      <div className='tabContent'>
        <div className='mainView'>
          <Routes>
            <Route path="/"              element={ Dashboard  ()  } />
            <Route path="/flowboard"     element={ Dashboard  ()  } />
            {/* <Route path="/analysisboard" element={ Chartboard ()  } /> */}
            <Route path="/throughput"    element={ Throughput ()  } />
            <Route path="/settings"      element={ Settings   ()  } />
            <Route path="/analysisboard" element={<AppNew/>} />
            <Route path="*"              element={ <div>404</div> } />
          </Routes>
        </div>
        {Filter ()}
      </div>
    </div>
  );
}

let wsConnect = async (wsEndpointURL: string, runId: string, dispatch: AppDispatch) => {
  socket = io (wsEndpointURL, { autoConnect: true });

  socket.on ('connect', () => {
    dispatch (changeSocket (true));

    // send pings to track latency every 10 seconds
    if (interval === undefined) {
      interval = setInterval (() => {
        let resetCounter = 0;
        if (lastPing === undefined) {
          // first ping
          socket.emit ('ping');
          dispatch (setLastPing (new Date().getTime()));
        } else {
          // only emit once the last pong is bigger than the last ping
          // if ~30 seconds pass without a pong, ping again
          if ((lastPong !== undefined && lastPong > lastPing) || resetCounter >= 3) {
            socket.emit ('ping');
            dispatch (setLastPing (new Date().getTime()));
            resetCounter = 0
          } else {
            resetCounter++;
          }
        }
      }, 10000);
    }
  });

  socket.on ('disconnect', () => {
    dispatch (changeSocket  (false));
    clearInterval (interval);
  });

  socket.on ('connect_error', function (err) {
    const message = "Cannot conntect to " + wsEndpointURL + " ... " + err
    console.log ("Websocket Error " + message);
  });

  socket.on ('mlgym_event', (msg: string) => {
    let parsedMsg = {
      event_type : "unknown" as supportedEvents,
      payload    : {}
    };

    try {
      parsedMsg = JSON.parse (msg);
    } catch (e: unknown) {
      let error = e as unknown as Error;
      console.log ("Websocket Error " + error.message);
    }

    const eventType: supportedEvents = parsedMsg["event_type"];
    let data = parsedMsg["payload"] as serverJob | serverExpriment;
    let dispatchData: Experiment | Job | undefined = undefined;

    if (supportedEvents.indexOf (eventType) > -1) {
      try {
        switch (eventType) {
          case "job_status":        dispatchData = convertJob        (data as serverJob,       eventType); break;
          case "job_scheduled":     dispatchData = convertJob        (data as serverJob,       eventType); break;
          case "evaluation_result": dispatchData = convertExperiment (data as serverExpriment, eventType); break;
          case "experiment_config": dispatchData = convertExperiment (data as serverExpriment, eventType); break;
          case "experiment_status": dispatchData = convertExperiment (data as serverExpriment, eventType); break;
          default: throw ("Unknown eventType");
        }
      } catch (e: unknown) {
        let error = e as unknown as Error;
        console.log ("Parsing Error " + error);
      }

      // --- this is not great if new event types are added
      if (dispatchData !== undefined) {
        if (eventType.includes ("job")) {
          // dispatch to state of jobs
          dispatch (upsertJob (dispatchData as Job));
        } else if (eventType.includes ("experiment") || eventType.includes ("evaluation")) {
          // disptach to state of exps
          dispatch (upsertExp (dispatchData as Experiment));
        }
      }
    } else {
      const message = "WARNING: eventy type " + eventType + " not supported!"
      console.log ("Websocket Error " + message);
    }
  });

  socket.on('pong', () => {
    dispatch (setLastPong (new Date ().getTime ()));
  });
}

export default App;