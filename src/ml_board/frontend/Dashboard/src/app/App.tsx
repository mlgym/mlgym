import * as React from 'react';
import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { saveEvalResultData } from '../redux/experiments/experimentsSlice';
import DedicatedWorker from '../webworkers/DedicatedWorker';
import './App.scss';

// import Filter from '../components/filter/Filter';
import { upsertExperiment } from '../redux/experiments/yetAnotherExperimentSlice';
import { upsertJob } from '../redux/jobs/jobSlice';
import { DataToRedux } from '../webworkers/worker_utils';
import { useAppDispatch } from './hooks';
import TopBarWithDrawer from '../components/topbar-with-drawer/TopBarWithDrawer';
import Drawer from '@mui/material/Drawer';
import ScrollToTop from '../components/scroll-to-top/ScrollToTop';
import { RoutesMapping } from './RoutesMapping';
import Fab from '@mui/material/Fab';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import TextareaAutosize from '@mui/material/TextareaAutosize';
import Button from '@mui/material/Button';
import CloseIcon from '@mui/icons-material/Close';
import CheckIcon from '@mui/icons-material/Check';
import Stack from '@mui/material/Stack';
import Zoom from '@mui/material/Zoom';
import { useLocation } from "react-router-dom";
import TextField from '@mui/material/TextField';

export default function App() {

    const [state, setState] = useState({
        bottom: false
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

    const applyFilter = () => {
        setState({ ...state, ["bottom"]: false });
    }

    return (
        <div className="App">
            <ScrollToTop />
            {
                urls.includes(location.pathname.split("/")[1]) ?
                <TopBarWithDrawer/>
                :
                null
            }
            <Routes>
                {
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
                urls.includes(location.pathname.split("/")[1]) ?
                <Zoom in={true}>
                    <Fab
                        sx={{
                            position: "fixed",
                            bottom: (theme) => theme.spacing(2),
                            right: (theme) => theme.spacing(2)
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
                            paddingRight: "20px"
                        }
                    }}
                >
                    <h3>
                        Filter Results
                    </h3>
                    <TextField
                        id="outlined-multiline-flexible"
                        label="Filter"
                        placeholder="Filter your experiments here!..."
                        multiline
                        maxRows={4}
                    />
                    <Stack 
                        direction="row" 
                        spacing={5}
                        sx={{
                            marginTop: "20px",
                            marginBottom: "30px"
                        }}
                    >
                        <Button 
                            variant="contained" 
                            startIcon={<CheckIcon />}
                            onClick={()=>applyFilter()}
                            sx={{
                                width: "20%"
                            }}
                        >
                            Apply
                        </Button>
                        <Button 
                            variant="contained" 
                            endIcon={<CloseIcon />}
                            onClick={toggleDrawer("bottom", false)}
                            sx={{
                                width: "20%"
                            }}
                        >
                            Cancel
                        </Button>
                    </Stack>
                </Drawer>
            </React.Fragment>
        </div>
    );
}