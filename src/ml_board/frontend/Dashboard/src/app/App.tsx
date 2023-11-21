import { useEffect, useState } from 'react';
import { Route, Routes, useSearchParams } from 'react-router-dom';
import { resetChartState, upsertCharts } from '../redux/charts/chartsSlice';
import { incrementReceivedMsgCount, selectTab, setGridSearchId, setLastPing, setRestApiUrl, setSocketConnection, setSocketConnectionUrl, setThroughput } from '../redux/globalConfig/globalConfigSlice';
import { resetTableState, upsertManyRows, upsertTableHeaders } from '../redux/table/tableSlice';
import { DataToRedux } from '../worker_socket/DataTypes';
import { RoutesMapping } from './RoutesMapping';
import { useAppDispatch, useAppSelector } from './hooks';

// components & styles
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import ConfigPopup from '../components/configPopup/ConfigPopup';
import Settings from '../components/settings/Settings';
import TopBarWithDrawer from '../components/topbar-with-drawer/TopBarWithDrawer';
import styles from './App.module.css';
import { Toolbar } from '@mui/material';




import file from "../components/modelCard/flowGraph/mock/data.js";
import FlowGraph from '../components/modelCard/flowGraph/FlowGraph';
import { createGraphWithoutRoot } from '../components/modelCard/flowGraph/api';
import { ReactFlowProvider } from 'reactflow';


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
    if (settingConfigsInStorage) {
        settingConfigs = await JSON.parse(settingConfigsInStorage);
    }

    if (gridSearchId !== null) {
        settingConfigs.gridSearchId = gridSearchId;
    }

    if (socketConnectionUrl !== null) {
        settingConfigs.socketConnectionUrl = socketConnectionUrl;
    }

    if (restApiUrl !== null) {
        settingConfigs.restApiUrl = restApiUrl;
    }

    return settingConfigs;
}

export default function App() {

    const { nodes, edges } = createGraphWithoutRoot(file);

    console.log(nodes.length);
    console.log(edges.length);

    return (
        <ReactFlowProvider>
            <FlowGraph initialNodes={nodes} initialEdges={edges} />
        </ReactFlowProvider>
    );

    const [isConfigValidated, setConfigValidation] = useState(false);
    const [socketConnectionRequest, setSocketConnectionRequest] = useState(false);
    const [connectionSnackBar, setConnectionSnackBar] = useState({
        isOpen: false,
        connection: false
    });
    const tab = useAppSelector(selectTab);
    const dispatch = useAppDispatch();
    const [searchParams, setSearchParams] = useSearchParams();
    const [settingConfigs, setSettingConfigs] = useState({
        gridSearchId: "",
        socketConnectionUrl: "",
        restApiUrl: ""
    });

    useEffect(() => {
        // Await key used in this function - suspends execution of the code below it and assures that it does it's task and returns valaue -- this is called promise (from a function). So as the function is executed, it returns a promise with data which must be accessed like this:
        getUrlParamsOrLocalStorageData(searchParams, settingConfigs).then((settingConfigs) => {
            setSettingConfigs(settingConfigs);
            localStorage.setItem('SettingConfigs', JSON.stringify(settingConfigs));
        });
    }, []);

    const urls: Array<string> = [];
    Object.keys(RoutesMapping).forEach((routeMapKey) => {
        if (routeMapKey !== "ErrorComponent") {
            urls.push(RoutesMapping[routeMapKey].url);
        }
    });

    useEffect(() => {
        if (socketConnectionRequest) {
            dispatch(resetChartState());
            dispatch(resetTableState());
            // save to local storage only after user clicks on submit button - either in popup or in settings page.
            // after the used submits the values & after it is saved, then only we will connect to the socket with the values given by user.
            // TODO:: after Vijul and Osama's code is merged, handle error message from the socket and show to user - so if the socket connection was not successful, user can update the values and try again.
            localStorage.setItem('SettingConfigs', JSON.stringify(settingConfigs));

            // creating WebWorker
            // NOTE:using URL because create-react-app throws error since it has not found the worker file during load/bundling
            const workerSocket = new Worker(new URL('../worker_socket/WorkerSocket.ts', import.meta.url));
            // setting the redux update methods on the incoming data from the worker thread
            workerSocket.onmessage = ({ data }: MessageEvent) => workerOnMessageHandler(data as DataToRedux, workerSocket);
            // starting the worker
            workerSocket.postMessage(settingConfigs);

            // close the worker on Dismount to stop any memory leaks
            return () => {
                workerSocket.postMessage("CLOSE_SOCKET");
                workerSocket.terminate();
            }
        }
    }, [socketConnectionRequest, settingConfigs]);
    // recommended way: keeping the second condition blank, fires useEffect just once as there are no conditions to check to fire up useEffect again (just like componentDidMount of React Life cycle).


    // TODO: maybe useCallback, how many times does App get rendered???
    // NOTE: data is alway created with 2 empty buffers and then populated before being passed to this method, so no need to check for null or undefined!
    const workerOnMessageHandler = (data: DataToRedux, workerSocket: Worker) => {
        if (data.status) {
            if (data.status.isSocketConnected === false) {
                setConnectionSnackBar({
                    isOpen: true,
                    connection: data.status["isSocketConnected"]
                });

                dispatch(setSocketConnection(data.status["isSocketConnected"]));
                dispatch(resetChartState());
                dispatch(resetTableState());

                workerSocket.terminate();

                setConfigValidation(false);
            }
            else if (data.status.isSocketConnected === true) {
                setConnectionSnackBar({
                    isOpen: true,
                    connection: data.status["isSocketConnected"]
                });

                dispatch(setSocketConnection(data.status.isSocketConnected));
                dispatch(setGridSearchId(data.status.gridSearchId));
                dispatch(setRestApiUrl(data.status.restApiUrl));
                dispatch(setSocketConnectionUrl(settingConfigs.socketConnectionUrl));
                // dispatch(setSocketConnectionUrl(data.status["restApiUrl"]));

                setConfigValidation(true);
            }
            else if (data.status === "msg_count_increment") {
                dispatch(incrementReceivedMsgCount());
            }
            else if (data.status.ping !== undefined) {
                dispatch(setLastPing(data.status["ping"]));
            }
            else if (data.status.throughput !== undefined) {
                dispatch(setThroughput(data.status["throughput"]));
            }
        } else if (data.chartsUpdates.length > 0) {
            // update the Charts Slice
            dispatch(upsertCharts(data.chartsUpdates!));
            dispatch(upsertManyRows(data.tableData!));
            dispatchTableHeadersUpdate(data.tableHeaders);
        } else if (data.tableData.length > 0) {
            dispatch(upsertManyRows(data.tableData!));
            dispatchTableHeadersUpdate(data.tableHeaders);
        }
    }

    function dispatchTableHeadersUpdate(tableHeaders: Array<string> | undefined) { tableHeaders && dispatch(upsertTableHeaders(tableHeaders)); }

    return (
        <div className={styles.main_container}>
            {
                // Show TopBar only if valid url is there. For example, if we get unregistered url (i.e 404 error) then don't show the TopBar
                urls.includes(tab) && <TopBarWithDrawer />
            }
            {
                // Show TopBar only if valid url is there. For example, if we get unregistered url (i.e 404 error) then don't show the TopBar
                urls.includes(tab) && <Toolbar />
            }
            <Routes>
                {
                    // Dynamic Routes added as a functionality. 
                    // Rendering Names as per routes helps in Menu also. So, to keep the Component and Route name mapping uniform, RoutesMapping.tsx is the single file to look at for any updates or changes to be made
                    Object.keys(RoutesMapping).map((routeMapKey, index) => {
                        // If the settings page is to render, we have to do it seperately from dynamic routing as we need to pass functions as props to settings page - so that when user submits the configured values, we can connect to websocket with the changed parameters.
                        if (routeMapKey === "Settings") {
                            return (
                                <Route
                                    key={index}
                                    path={RoutesMapping[routeMapKey].url}
                                    element={
                                        <Settings
                                            setSocketConnectionRequest={() => setSocketConnectionRequest(true)}
                                            setConfigData={(settingConfigs: settingConfigsInterface) => setSettingConfigs(settingConfigs)}
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
                // here also, it is same as done above for Setting Component. We need to pass functions as props to the popup - so that when user submits the configured values, we can connect to websocket with the changed parameters.
                urls.includes(tab) && tab !== RoutesMapping["Settings"].url && isConfigValidated === false ?
                    <ConfigPopup
                        isConfigValidated={isConfigValidated}
                        setSocketConnectionRequest={() => setSocketConnectionRequest(true)}
                        setConfigData={(settingConfigs: settingConfigsInterface) => setSettingConfigs(settingConfigs)}
                    />
                    :
                    null
            }
            {/* Socket connection success / fail message temperory popup which will disappeaer in 4secs or when closed manually by user */}
            <Snackbar
                anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
                open={connectionSnackBar.isOpen}
                onClose={() => setConnectionSnackBar({ ...connectionSnackBar, isOpen: false })}
                autoHideDuration={3000}
            >
                <Alert
                    onClose={() => setConnectionSnackBar({ ...connectionSnackBar, isOpen: false })}
                    severity={connectionSnackBar.connection ? "success" : "error"}
                >
                    {`Socket Connection ${connectionSnackBar.connection ? "Successful" : "Failed"}`}
                </Alert>
            </Snackbar>
        </div>
    );
}