import { Component } from 'react';
import { connect } from 'react-redux';
import { Route, Routes } from 'react-router-dom';
import Graphs from '../components/graphs/Graphs';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import { upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { changeSocketConnection } from '../redux/status/statusSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import { reduxData } from '../webworkers/event_handlers/evaluationResultDataHandler';
import './App.scss';

import Dashboard from '../components/dashboard/Dashboard';
import Filter from '../components/filter/Filter';
import Settings from '../components/settings/Settings';
import Throughput from '../components/throughputs/Throughput';
import Tabs from '../ui/tabs/Tabs';
import { DataToRedux } from '../webworkers/worker_utils';

type AppProps = {
    evalResult: reduxData
    saveEvalResultData: Function
    upsertJob:Function
    upsertExperiment:Function
}

type AppInterface = {
    mlgymWorker:DedicatedWorker | null
}

class App extends Component<AppProps> implements AppInterface{
    
    mlgymWorker: DedicatedWorker | null
    isConnectingWebSocket: boolean = false;
    

    constructor(props: any) {
        super(props);
        this.mlgymWorker = null
    }

    // NOTE:
    // as per life cycle of react componentDidMount will execute first & will execute only once regardless of the props / redux updates. [in functional components, as any of the props / redux updates, the whole functional component is refreshed again].
    // if we use functional component, then the page refreshes again and again due to constant redux updates. So it will cause to create new worker & socket connection everytime forever - going into infinte loop, & thus will crash the app.
    // so, here we use the class component - which follows the react lifecycle & limiting the page refresh to just once i.e. on screen load / reload.
    componentDidMount() {
        if (!this.isConnectingWebSocket) {
            this.createWorker();
            this.isConnectingWebSocket = true;
        }
    }

    render() {
        return(
            <div className="App">
                <Tabs/>
                <div className='tabContent'>
                    <div className='mainView'>
                        <Routes>
                        <Route path="/"              element={ <Graphs/> } />
                        <Route path="/analysisboard" element={ <Graphs/> } />
                        <Route path="/dashboard"     element={ <Dashboard/> } />
                        <Route path="/throughput"    element={ <Throughput/>  } />
                        <Route path="/settings"      element={ <Settings/>  } />
                        <Route path="*"              element={ <div>404</div> } />
                        </Routes>
                    </div>
                    <Filter/>
                </div>
            </div>
        )
    }

    createWorker = () => {
        // TODO: is DedicatedWorker really needed? 
        this.mlgymWorker = new DedicatedWorker(Object(this.workerOnMessageHandler));
        this.mlgymWorker.postMessage(this.props.evalResult);
    }

    // ASK Vijul: Why the 'async'?
    workerOnMessageHandler = async(data: DataToRedux|string) => {
        if (typeof(data) === "string") {
            console.log(data);
        }
        else
        {
            if(data && data.evaluationResultsData)
            {
                // ASK Vijul: Why the 'await'? (in case we get update request at the same time the state is being updated)
                await this.props.saveEvalResultData(data.evaluationResultsData);
            }
            else if(data && data.jobStatusData)
            {
                this.props.upsertJob(data.jobStatusData)
            }
            else if(data && data.experimentStatusData)
            {
                this.props.upsertExperiment(data.experimentStatusData)
            }
        }
    }
}

const mapStateToProps = (state: any) => ({
    evalResult: state.experimentsSlice.evalResult,
    isWebSocketConnected: state.status.wsConnected,
});

const mapDispatchToProps = { saveEvalResultData, changeSocketConnection, upsertJob, upsertExperiment };

export default connect(mapStateToProps, mapDispatchToProps)(App);