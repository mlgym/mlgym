import * as React from 'react';
import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import './App.scss';
import { upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { DataToRedux } from '../webworkers/worker_utils';
import { useAppDispatch } from './hooks';
import TopBarWithDrawer from '../components/topbar-with-drawer/TopBarWithDrawer';
import Drawer from '@mui/material/Drawer';
import { RoutesMapping } from './RoutesMapping';
import Fab from '@mui/material/Fab';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import Zoom from '@mui/material/Zoom';
import { useLocation } from "react-router-dom";
import TextField from '@mui/material/TextField';

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
            colors_mapped_to_exp_id: [[],[]]
        }
        mlgymWorker.postMessage(evalResult);

        // TODO: close the worker here?
        // return () =>{ }
    }, []) // recommended way: keeping the second condition blank, fires useEffect just once as there are no conditions to check to fire up useEffect again (just like componentDidMount of React Life cycle). 

    // TODO: maybe useCallback
    const workerOnMessageHandler = (data: DataToRedux) => {
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
            else if(data && data.experimentStatusData)
            {
                dispatch(upsertExperiment(data.experimentStatusData))
            }
        }
    }

    const toggleDrawer = (anchor: string, open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (event.type === 'keydown' && ((event as React.KeyboardEvent).key === 'Tab' || (event as React.KeyboardEvent).key === 'Shift')) {
            return;
        }
        setState({ ...state, [anchor]: open });
    }

    function changeFilterText (text:string) {
        setState({ ...state, ["filterText"]: text });
    }

    return (
        <div className="App">
            {
                urls.includes(location.pathname.split("/")[1]) ?
                // Show TopBar only if valid url is there. For example, if we get unregistered url (i.e 404 error) then don't the TopBar
                <TopBarWithDrawer/>
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
                        onChange={(e)=>changeFilterText(e.target.value)}
                    />
                </Drawer>
            </React.Fragment>
        </div>
    );
}