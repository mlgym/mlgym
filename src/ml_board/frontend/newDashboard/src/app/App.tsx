import { Component } from 'react';
import Graphs from '../components/graphs/Graphs';
import { Route,Routes }    from 'react-router-dom';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import { connect } from 'react-redux';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import { reduxState } from '../redux/store';
import EVENT_TYPE from '../webworkers/socketEventConstants';
import { evalResultCustomData } from '../webworkers/event_handlers/evaluationResultDataHandler';
import './App.scss';

import Filter              from '../components/filter/Filter';
import Dashboard           from '../components/dashboard/Dashboard';
import Settings            from '../components/settings/Settings';
import Throughput          from '../components/throughputs/Throughput';
import Tabs                from '../ui/tabs/Tabs';

type AppProps = {
    evalResult: evalResultCustomData
    saveEvalResultData: Function
}

type AppState = {
    
}

type AppInterface = {
    mlgymWorker: {
        DedicatedWorker: {
            onMessageCtxNFunc: Function,
            worker: Worker
        }
    }
}

type postMessageData = {
    dataToUpdateReduxInChart: evalResultCustomData,
    dataToUpdateReduxInDashboard: {

    }
} | string

class App extends Component<AppProps, AppState> implements AppInterface{
    
    mlgymWorker: any
    
    constructor(props: AppProps) {
        super(props);
        this.mlgymWorker = null
    }

    // NOTE:
    // as per life cycle of react componentDidMount will execute first & will execute only once regardless of the props / redux updates. [in functional components, as any of the props / redux updates, the whole functional component is refreshed again].
    // if we use functional component, then the page refreshes again and again due to constant redux updates. So it will cause to create new worker & socket connection everytime forever - going into infinte loop, & thus will crash the app.
    // so, here we use the class component - which follows the react lifecycle & limiting the page refresh to just once i.e. on screen load / reload.
    componentDidMount() {
        this.createWorker();
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
        this.mlgymWorker = new DedicatedWorker(Object(this.workerOnMessageHandler));
        this.mlgymWorker.postMessage(this.props.evalResult);
    }

    workerOnMessageHandler = async(data: postMessageData) => {
        if (typeof(data) === "string") {
            if(data === EVENT_TYPE.SOCKET_CONN_SUCCESS)
            {
                console.log(EVENT_TYPE.SOCKET_CONN_SUCCESS);
            }
            else
            {
                console.log(EVENT_TYPE.SOCKET_CONN_FAIL);
            }    
        }
        else
        {
            if(data && data.dataToUpdateReduxInChart)
            {
                switch(data.dataToUpdateReduxInChart.event_type) {
                    case EVENT_TYPE.JOB_STATUS:
                        
                        break;
                    case EVENT_TYPE.JOB_SCHEDULED:
                        
                        break;
                    case EVENT_TYPE.EVALUATION_RESULT:
                        await this.props.saveEvalResultData(data.dataToUpdateReduxInChart);
                        console.log("Data from redux = ",this.props.evalResult);
                        break;
                    case EVENT_TYPE.EXPERIMENT_CONFIG:
                        
                        break;
                    case EVENT_TYPE.EXPERIMENT_STATUS:
                        
                        break;
                    default: throw new Error(EVENT_TYPE.UNKNOWN_EVENT); 
                }
            }
            else if(data && data.dataToUpdateReduxInDashboard)
            {
                // TODO: Save to redux like above
            }
        }
    }
}

const mapStateToProps = (state: reduxState) => ({
    evalResult: state.experimentsSlice.evalResult
});

const mapDispatchToProps = { saveEvalResultData };

export default connect(mapStateToProps, mapDispatchToProps)(App);