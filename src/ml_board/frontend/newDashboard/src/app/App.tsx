import { Component } from 'react';
import Graphs from '../components/graphs/Graphs';
import { Route,Routes }    from 'react-router-dom';
import DedicatedWorkerClass from '../webworkers/DedicatedWorker';
import { connect } from 'react-redux';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import './App.scss';

import Filter              from '../components/filter/Filter';
import Dashboard           from '../components/dashboard/Dashboard';
import Settings            from '../components/settings/Settings';
import Throughput          from '../components/throughputs/Throughput';
import Tabs                from '../ui/tabs/Tabs';

type AppProps = {
    evalResult: any
    saveEvalResultData: Function
}

type AppState = {
    
}

type AppInterface = {
    mlgymWorker: any
}

class App extends Component<AppProps, AppState> implements AppInterface{
    
    mlgymWorker: any
    
    constructor(props: any) {
        super(props);
        this.mlgymWorker = null;
    }

    // NOTE:
    // as per life cycle of react componentDidMount will execute first & will execute only once regardless of the props / redux updates. [in functional components, as any of the props / redux updates, the whole functional component is refreshed again].
    // if we use functional component, then the page refreshes again and again due to constant redux updates. So it will cause to create new worker & socket connection everytime forever - going into infinte loop, & thus will crash the app.
    // so, here we use the class component - which follows the react lifecycle & limiting the page refresh to just once i.e. on screen load / reload.
    componentDidMount() {
        localStorage.clear();
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
        this.mlgymWorker = new DedicatedWorkerClass(Object(this.workerOnMessageHandler));
        this.mlgymWorker.postMessage(this.props.evalResult);
    }

    workerOnMessageHandler = async(data: any) => {
        if(data && data.dataToUpdateReduxInChart && data.dataToUpdateReduxInChart.grid_search_id !== null && data.dataToUpdateReduxInChart.experiments !== undefined)
        {
            await this.props.saveEvalResultData(data.dataToUpdateReduxInChart);
            console.log("Data from redux = ",this.props.evalResult);
        }
        if(data && data.dataToUpdateReduxInDashboard)
        {
            // TODO: Save to redux like above
        }
    }
}

const mapStateToProps = (state: any) => ({
    evalResult: state.experimentsSlice.evalResult
});

const mapDispatchToProps = { saveEvalResultData };

export default connect(mapStateToProps, mapDispatchToProps)(App);