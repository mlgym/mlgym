import * as React from 'react';
import { useEffect, useState } from 'react';
import { Route, Routes, useLocation, useSearchParams } from 'react-router-dom';
import TopBarWithDrawer from '../components/topbar-with-drawer/TopBarWithDrawer';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import { updateExperiment, upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { incrementReceivedMsgCount, setLastPing, setSocketConnection, setThroughput } from '../redux/status/statusSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import { EvaluationResultPayload } from '../webworkers/event_handlers/evaluationResultDataHandler';
import { DataToRedux } from '../webworkers/worker_utils';
import { useAppDispatch } from './hooks';
import { RoutesMapping } from './RoutesMapping';
import { SOCKET_STATUS } from '../webworkers/socketEventConstants';

// styles
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import Drawer from '@mui/material/Drawer';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import styles from './App.module.css';
import ConfigPopup from '../components/configPopup/ConfigPopup';
import Settings from '../components/settings/Settings';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

export interface settingConfigsInterface {
    gridSearchId: string,
    socketConnectionUrl: string,
    restApiUrl: string
}

// function to get parameters from url or localstorage to show them populated on the popup or in the settings page.
// function is made async as JSON parsing needs to be done asynchronously for fetching data from local storage and then set in `settingConfigs` key-values. Then if the url params are present, they will overwrite local storage values.
async function getUrlParamsOrLocalStorageData(searchParams: URLSearchParams, settingConfigs: settingConfigsInterface) {
    let gridSearchId = searchParams.get("run_id")
    let socketConnectionUrl = searchParams.get("ws_endpoint")
    let restApiUrl = searchParams.get("rest_endpoint")

    let settingConfigsInStorage = localStorage.getItem('SettingConfigs');
    if(settingConfigsInStorage) {
        settingConfigs = await JSON.parse(settingConfigsInStorage);
    }

    // in the else parts below: for now, I kept default values if the server is localhost or 127.0.0.1 - so we have ease in development. Let me know if it needs to be changed.
    if(gridSearchId !== null) {
        settingConfigs.gridSearchId = gridSearchId;
    }
    else if(!settingConfigsInStorage && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
        settingConfigs.gridSearchId = "mlgym_event_subscribers";
    }
    
    if(socketConnectionUrl !== null) {
        settingConfigs.socketConnectionUrl = socketConnectionUrl;
    }
    else if(!settingConfigsInStorage && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
        settingConfigs.socketConnectionUrl = "http://"+window.location.hostname+":7000/";
    }

    if(restApiUrl !== null) {
        settingConfigs.restApiUrl = restApiUrl;
    }
    else if(!settingConfigsInStorage && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
        settingConfigs.restApiUrl = "http://"+window.location.hostname+":5001/";
    }

    return settingConfigs;
}

export default function App() {

    const [filterText, setFilterText] = useState("")
    const [filterDrawer, setFilterDrawer] = useState(false)
    const [isConfigValidated, setConfigValidation] = useState(false)
    const [configChangeDetectionCounter, setConigChangeDetectionCounter] = useState(0)
    const [isSnackbarOpen, setSnackbarOpen] = useState(false)
    const [snackBarText, setSnackBarText] = useState("")
    const location = useLocation();
    const dispatch = useAppDispatch();
    const [searchParams, setSearchParams] = useSearchParams();
    const [settingConfigs, setSettingConfigs] = useState({
        gridSearchId: "",
        socketConnectionUrl: "",
        restApiUrl: ""
    })

    useEffect(() => {
        // Await key used in this function - suspends execution of the code below it and assures that it does it's task and returns valaue -- this is called promise (from a function). So as the function is executed, it returns a promise with data which must be accessed like this:
        getUrlParamsOrLocalStorageData(searchParams, settingConfigs).then((settingConfigs)=>{
            setSettingConfigs(settingConfigs);
            localStorage.setItem('SettingConfigs', JSON.stringify(settingConfigs));
        });
    },[])

    const urls: Array<string> = [];
    Object.keys(RoutesMapping).forEach((routeMapKey) => {
        if (routeMapKey !== "ErrorComponent") {
            urls.push(RoutesMapping[routeMapKey].url);
        }
    });

    useEffect(() => {
        if(isConfigValidated && configChangeDetectionCounter !== 0)
        {
            // save to local storage only after user clicks on submit button - either in popup or in settings page.
            // after the used submits the values & after it is saved, then only we will connect to the socket with the values given by user.
            // TODO:: after Vijul and Osama's code is merged, handle error message from the socket and show to user - so if the socket connection was not successful, user can update the values and try again.
            localStorage.setItem('SettingConfigs', JSON.stringify(settingConfigs));

            // TODO: is DedicatedWorker really needed? 
            const mlgymWorker = new DedicatedWorker(workerOnMessageHandler);
            // NOTE: this is better than calling "useAppSelector(selectEvalResult)" as it will force the App function to get called everytime the state changes
            // TODO: maybe find a better way later other than starting the worker with the empty redux state?
            const evalResult = {
                grid_search_id: null,
                experiments: {},
                colors_mapped_to_exp_id: [[], []]
            }
            mlgymWorker.postMessage({evalResult, settingConfigs});
            // TODO: close the worker here?
            // return () =>{ }
        }
    }, [isConfigValidated,configChangeDetectionCounter]) 
    // recommended way: keeping the second condition blank, fires useEffect just once as there are no conditions to check to fire up useEffect again (just like componentDidMount of React Life cycle). 

    // TODO: maybe useCallback
    function workerOnMessageHandler (data: DataToRedux) {
        if (typeof (data) === "string") {
            // TODO: this is not correct, try running the frontend without a backend to connect to it would still say "Socket Connection Successful"
            // this is solved in the stash "DedicatedWorker redundancy" push it after solving the mystery of initial redux state!
            console.log(data);
            if(data === SOCKET_STATUS.SOCKET_CONN_SUCCESS) {
                setSnackBarText(SOCKET_STATUS.SOCKET_CONN_SUCCESS);
                setSnackbarOpen(true);
            }
            else {
                setSnackBarText(SOCKET_STATUS.SOCKET_CONN_FAIL);
                setSnackbarOpen(true);
            }
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
    
    return (
        <div className={styles.main_container}>
            {
                // Show TopBar only if valid url is there. For example, if we get unregistered url (i.e 404 error) then don't show the TopBar
                urls.includes(location.pathname.split("/")[1]) && <TopBarWithDrawer />
            }
            <Routes>
                {
                    // Dynamic Routes added as a functionality. 
                    // Rendering Names as per routes helps in Menu also. So, to keep the Component and Route name mapping uniform, RoutesMapping.tsx is the single file to look at for any updates or changes to be made
                    Object.keys(RoutesMapping).map((routeMapKey, index) => {
                        // If the settings page is to render, we have to do it seperately from dynamic routing as we need to pass functions as props to settings page - so that when user submits the configured values, we can connect to websocket with the changed parameters.
                        if(routeMapKey === "Settings") {
                            return (
                                <Route
                                    key={index}
                                    path={RoutesMapping[routeMapKey].url}
                                    element={
                                        <Settings
                                            validateConfigs={(value:boolean)=>setConfigValidation(value)} 
                                            setConfigChangeDetectionCounter={()=>setConigChangeDetectionCounter(configChangeDetectionCounter+1)}
                                            setConfigData={(settingConfigs: settingConfigsInterface)=>setSettingConfigs(settingConfigs)}
                                        />
                                    }
                                />
                            )
                        }
                        else {
                            return (
                                <Route
                                    key={index}
                                    path={RoutesMapping[routeMapKey].url}
                                    element={RoutesMapping[routeMapKey].component}
                                />
                            )
                        }
                    })
                }
            </Routes>
            {
                // Floating Action Button (FAB) added for filter popup
                // Show filter - FAB only if valid url is there. Else hide the button (Just as mentioned above - for the case of TopBar). Also hide it when user is on Settings Page (As - not needed to do filter when viewing/inserting/updating configurations)
                urls.includes(location.pathname.split("/")[1]) && location.pathname.split("/")[1] !== RoutesMapping["Settings"].url ?
                <div className={styles.fab}>
                    <Fab
                        variant="extended"
                        color="primary"
                        aria-label="add"
                        onClick={() => setFilterDrawer(true)}
                    >
                        <FilterAltIcon /> Filter
                    </Fab>
                </div>
                :
                null
            }
            {/* Filter Popup */}
            <React.Fragment>
                <Drawer
                    anchor={"bottom"} // MUI-Drawer property: tells from which side of the screen, the drawer should appear
                    open={filterDrawer}
                    onClose={() => setFilterDrawer(false)}
                    // Drawer wraps your content inside a <Paper /> component. A Materiaul-UI paper component has shadows and a non-transparent background.
                    classes={{ paper: styles.filter_drawer_container }}
                >
                    <div className={styles.filter_container}>
                        <h3>
                            Filter Your Results
                        </h3>
                        <TextField
                            id="outlined-multiline-flexible"
                            label="Filter"
                            placeholder="Filter your experiments here!..."
                            multiline
                            maxRows={4}
                            value={filterText}
                            onChange={(e) => setFilterText(e.target.value)}
                            className={styles.filter_textfield}
                        />
                    </div>
                </Drawer>
            </React.Fragment>
            {
                // here also, it is same as done above for Setting Component. We need to pass functions as props to the popup - so that when user submits the configured values, we can connect to websocket with the changed parameters.
                urls.includes(location.pathname.split("/")[1]) && location.pathname.split("/")[1] !== RoutesMapping["Settings"].url && isConfigValidated === false &&configChangeDetectionCounter === 0 ?
                <ConfigPopup 
                    validateConfigs={(value:boolean)=>setConfigValidation(value)} 
                    setConfigChangeDetectionCounter={()=>setConigChangeDetectionCounter(configChangeDetectionCounter+1)}
                    setConfigData={(settingConfigs:settingConfigsInterface)=>setSettingConfigs(settingConfigs)}
                />
                :
                null
            }
            {/* Socket connection success / fail message temperory popup which will disappeaer in 4secs or when closed manually by user */}
            <Snackbar
                anchorOrigin={{ vertical:"bottom", horizontal:"center" }}
                open={isSnackbarOpen}
                onClose={()=>setSnackbarOpen(false)} 
                autoHideDuration={4000}
            >
                <Alert 
                    onClose={()=>setSnackbarOpen(false)} 
                    severity={snackBarText===SOCKET_STATUS.SOCKET_CONN_SUCCESS? "success": "error"}
                >
                    {snackBarText}
                </Alert>
            </Snackbar>
        </div>
    );
}