import { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import Graphs from '../components/graphs/Graphs';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import './App.scss';

import Dashboard from '../components/dashboard/Dashboard';
import Filter from '../components/filter/Filter';
import Settings from '../components/settings/Settings';
import Tabs from '../components/tabs/Tabs';
import Throughput from '../components/throughputs/Throughput';
import { upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { setLastPing, setLastPong } from '../redux/status/statusSlice';
import { DataToRedux } from '../webworkers/worker_utils';
import { useAppDispatch } from './hooks';


export default function App() {
    const dispatch = useAppDispatch();

    useEffect(() => {
        // TODO: is DedicatedWorker really needed? 
        const mlgymWorker = new DedicatedWorker(Object(workerOnMessageHandler));
        // NOTE: this is better than calling "useAppSelector(selectEvalResult)" as it will force the App function to get called everytime the state changes
        // TODO: maybe find a better way later other than starting the worker with the empty redux state?
        const evalResult = {
            grid_search_id: null,
            experiments: {},
            colors_mapped_to_exp_id: [[], []]
        }
        mlgymWorker.postMessage(evalResult);

        // TODO: close the worker here?
        // return () =>{ }
    }, [dispatch])

    // TODO: maybe useCallback
    const workerOnMessageHandler = (data: DataToRedux) => {
        if (typeof (data) === "string") {
            console.log(data);
        }
        else {
            if (data && data.evaluationResultsData && data.evaluationResultsData.grid_search_id !== null && data.evaluationResultsData.experiments !== undefined) {
                dispatch(saveEvalResultData(data.evaluationResultsData));
            }
            else if (data && data.jobStatusData) {
                dispatch(upsertJob(data.jobStatusData))
            }
            else if (data && data.experimentStatusData) {
                dispatch(upsertExperiment(data.experimentStatusData))
            }
            else if (data && data.status) {
                if (data.status["type"] === "PING") {
                    dispatch(setLastPing(data.status["time"]))
                } else if (data.status["type"] === "PONG") {
                    dispatch(setLastPong(data.status["time"]))
                }
            }
        }
    }

    return (
        <div className="App">
            <Tabs />
            <div className='tabContent'>
                <div className='mainView'>
                    <Routes>
                        <Route path="/" element={<Graphs />} />
                        <Route path="/analysisboard" element={<Graphs />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/throughput" element={<Throughput />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="*" element={<div>404</div>} />
                    </Routes>
                </div>
                <Filter />
            </div>
        </div>
    );
}