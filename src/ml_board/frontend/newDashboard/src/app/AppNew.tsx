import { Component } from 'react';
import Home from '../components/Home';
import DedicatedWorkerClass from '../webworkers/DedicatedWorker';
import { connect } from 'react-redux';
import { saveEvalResultData } from '../redux/actions/ExperimentActions';

type AppProps = {
    evalResult: any
    saveEvalResultData: Function
}

type AppState = {
    
}

type AppInterface = {
    mlgymWorker: any
}

class AppNew extends Component<AppProps, AppState> implements AppInterface{
    
    mlgymWorker: any
    
    constructor(props: any) {
        super(props);
        this.mlgymWorker = null;
    }

    componentDidMount() {
        localStorage.clear();
        this.createWorker();
    }

    render() {
        return(
            <Home/>
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
    evalResult: state.ExperimentsReducer.evalResult
});

const mapDispatchToProps = { saveEvalResultData };

export default connect(mapStateToProps, mapDispatchToProps)(AppNew);