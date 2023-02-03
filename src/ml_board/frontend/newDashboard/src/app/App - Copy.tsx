// export { };

import { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import Graphs from '../components/graphs/Graphs';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import './App.scss';

import Dashboard from '../components/dashboard/Dashboard';
import Filter from '../components/filter/Filter';
import Settings from '../components/settings/Settings';
import Throughput from '../components/throughputs/Throughput';
import { upsertJob } from '../redux/jobs/jobSlice';
import Tabs from '../ui/tabs/Tabs';
import { DataToRedux } from '../webworkers/worker_utils';
import { useAppDispatch } from './hooks';


export default function App() {

    const dispatch = useAppDispatch();
    // const evalResult = useAppSelector(selectEvalResult);
    // const evalResult = useSelector((state:RootState) => state.experimentsSlice.evalResult);
    
    useEffect(() => {
        // TODO: is DedicatedWorker really needed? 
        const mlgymWorker = new DedicatedWorker(Object(workerOnMessageHandler));
        const evalResult = {
            grid_search_id: null,
            experiments: {},
            colors_mapped_to_exp_id: [[],[]]
        }
        mlgymWorker.postMessage(evalResult);

        // TODO: close the worker here?
        // return () =>{ }
    }, [dispatch])

    // TODO: maybe useCallback
    const workerOnMessageHandler = (data: DataToRedux) => {
        console.log(data);
        if (typeof (data) === "string") {
            console.log(data);
        }
        else {
            if(data && data.evaluationResultsData && data.evaluationResultsData.grid_search_id !== null && data.evaluationResultsData.experiments !== undefined){
                dispatch(saveEvalResultData(data.evaluationResultsData));
            }
            else if (data && data.jobStatusData) {
                dispatch(upsertJob(data.jobStatusData))
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