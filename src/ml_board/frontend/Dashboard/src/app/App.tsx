import FilterAltIcon from '@mui/icons-material/FilterAlt';
import Drawer from '@mui/material/Drawer';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import Zoom from '@mui/material/Zoom';
import * as React from 'react';
import { useEffect, useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import TopBarWithDrawer from '../components/topbar-with-drawer/TopBarWithDrawer';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import { updateExperiment, upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { incrementReceivedMsgCount, setLastPing, setSocketConnection, setThroughput } from '../redux/status/statusSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import { EvaluationResultPayload } from '../webworkers/event_handlers/evaluationResultDataHandler';
import { DataToRedux } from '../webworkers/worker_utils';
import './App.scss';
import { useAppDispatch } from './hooks';
import { RoutesMapping } from './RoutesMapping';

export default function App() {

    const [state, setState] = useState({
        bottom: false,
        filterText: ""
    })
    const location = useLocation();
    const dispatch = useAppDispatch();

    const urls: Array<string> = [];
    Object.keys(RoutesMapping).map((routeMapKey) => {
        if (routeMapKey !== "ErrorComponent") {
            urls.push(RoutesMapping[routeMapKey].url);
        }
    });

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
    }, []) // recommended way: keeping the second condition blank, fires useEffect just once as there are no conditions to check to fire up useEffect again (just like componentDidMount of React Life cycle). 

    // TODO: maybe useCallback
    const workerOnMessageHandler = (data: DataToRedux) => {
        if (typeof (data) === "string") {
            // TODO: this is not correct, try running the frontend without a backend to connect to it would still say "Socket Connection Successful"
            // this is solved in the stash "DedicatedWorker redundancy" push it after solving the mystery of initial redux state!
            console.log(data);
        }
        else {
            if (data && data.evaluationResultsData) {
                // update the Charts Slice
                dispatch(saveEvalResultData(data.evaluationResultsData));
                // save the latest metric in the Experiment Slice
                const { epoch, experiment_id, metric_scores, loss_scores } = data.latest_split_metric as EvaluationResultPayload;
                const changes: { [latest_split_metric_key: string]: number } = {};
                for (const metric of metric_scores) {
                    changes[metric.split + "_" + metric.metric] = metric.score;
                }
                for (const loss of loss_scores) {
                    changes[loss.split + "_" + loss.loss] = loss.score;
                }
                //NOTE, I checked the epoch against the experiment's and that didn't work because of UseAppSelector! (can't be used here!)
                dispatch(updateExperiment({ id: experiment_id, changes: changes }))
            }
            else if (data && data.jobStatusData) {
                dispatch(upsertJob(data.jobStatusData))
            }
            else if (data && data.experimentStatusData) {
                dispatch(upsertExperiment(data.experimentStatusData))
            }
            else if (data && data.status) {
                if (data.status === "msg_count_increment") {
                    dispatch(incrementReceivedMsgCount())
                } else if (data.status["ping"] !== undefined) {
                    dispatch(setLastPing(data.status["ping"]))
                } else if (data.status["throughput"] !== undefined) {
                    dispatch(setThroughput(data.status["throughput"]))
                } else if (data.status["isSocketConnected"] !== undefined) {
                    dispatch(setSocketConnection(data.status["isSocketConnected"]))
                }
            }
        }
    }

    // ASK Vijul: Duplication ?
    const toggleDrawer = (anchor: string, open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (event.type === 'keydown' && ((event as React.KeyboardEvent).key === 'Tab' || (event as React.KeyboardEvent).key === 'Shift')) {
            return;
        }
        setState({ ...state, [anchor]: open });
    }

    function changeFilterText(text: string) {
        setState({ ...state, ["filterText"]: text });
    }

    return (
        <div className="App">
            {
                urls.includes(location.pathname.split("/")[1]) ?
                    // Show TopBar only if valid url is there. For example, if we get unregistered url (i.e 404 error) then don't the TopBar
                    <TopBarWithDrawer />
                    :
                    null
            }
            <Routes>
                {
                    // Dynamic Routes added as a functionality. 
                    // Rendering Names as per routes helps in Menu also. So, to keep the Component and Route name mapping uniform, RoutesMapping.tsx is the single file to look at for any updates or changes to be made
                    Object.keys(RoutesMapping).map((routeMapKey, index) => {
                        return (
                            <Route
                                key={index}
                                path={RoutesMapping[routeMapKey].url}
                                element={RoutesMapping[routeMapKey].component}
                            />
                        )
                    })
                }
            </Routes>
            {
                // Floating Action Button (FAB) added for filter popup
                // Show filter - FAB only if valid url is there. Else hide the button (Just as mentioned above - for the case of TopBar)
                urls.includes(location.pathname.split("/")[1]) ?
                    <Zoom in={true}>
                        <Fab
                            sx={{
                                position: "fixed",
                                bottom: (theme) => theme.spacing(6),
                                right: (theme) => theme.spacing(3),
                                opacity: 0.5,
                                ":hover": { opacity: 1 }
                            }}
                            variant="extended"
                            color="primary"
                            aria-label="add"
                            onClick={toggleDrawer("bottom", true)}
                        >
                            <FilterAltIcon /> Filter
                        </Fab>
                    </Zoom>
                    :
                    null
            }
            {/* Filter Popup */}
            <React.Fragment>
                <Drawer
                    anchor={"bottom"}
                    open={state["bottom"]}
                    onClose={toggleDrawer("bottom", false)}
                    PaperProps={{
                        style: {
                            borderTopLeftRadius: "10px",
                            borderTopRightRadius: "10px",
                            paddingLeft: "20px",
                            paddingRight: "20px",
                            paddingBottom: "30px"
                        }
                    }}
                >
                    <h3>
                        Filter Your Results
                    </h3>
                    <TextField
                        id="outlined-multiline-flexible"
                        label="Filter"
                        placeholder="Filter your experiments here!..."
                        multiline
                        maxRows={4}
                        value={state["filterText"]}
                        onChange={(e) => changeFilterText(e.target.value)}
                    />
                </Drawer>
            </React.Fragment>
        </div>
    );
}