import { Toolbar } from '@mui/material';
import { useAppSelector } from "../../app/hooks";
import { selectFilter, selectTableHeaders } from "../../redux/status/statusSlice";
import { useLocation } from 'react-router-dom';
import { selectAllRows } from "../../redux/table/tableSlice";
import Table from "./table/Table";
import { useState } from 'react';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import Fab from '@mui/material/Fab';
import styles from './Dashboard.module.css';
import { RoutesMapping } from '../../app/RoutesMapping';
import FilterTableHeaders from './filterTableHeaders/FilterTableHeaders';
import Zoom from '@mui/material/Zoom';
import ClearIcon from '@mui/icons-material/Clear';
import DragHandleIcon from '@mui/icons-material/DragHandle';
import SearchIcon from '@mui/icons-material/Search';
import FilterTextSearch from './filterTextSearch/FilterTextSearch';

export default function Dashboard() {
  
    // filter them based on the regEx in the status slice
    const re = new RegExp(useAppSelector(selectFilter));

    // fetch table data
    const rows = useAppSelector(selectAllRows);

    // fetch table headers
    let colNames: string[] = useAppSelector(selectTableHeaders);
    colNames = colNames.filter((colName: string) => re.test(colName));

    let [filterHeadersDrawer, setFilterHeadersDrawer] = useState(false);
    let [filterTextSearchDrawer, setFilterTextSearchDrawer] = useState(false);

    const location = useLocation();
    const urls: Array<string> = [];
    Object.keys(RoutesMapping).forEach((routeMapKey) => {
    if (routeMapKey !== "ErrorComponent") {
        urls.push(RoutesMapping[routeMapKey].url);
    }
    });

    const [isExpanded, setIsExpanded] = useState(false);

    const handleFabClick = () => {
        setIsExpanded(!isExpanded);
    };

    // Table should consist of these columns for minimized view. To get detailed view, user can click on the row and see the job + experiment details:
    // const colNames = ["experiment_id", "job_status", "starting_time", "finishing_time", "model_status", "epoch_progress", "batch_progress"];
    return (
        <div>
            <Toolbar />
            <Table colNames={colNames} rows={rows} />
            {
                // Floating Action Button (FAB) added for filter popup
                // Show filter - FAB only if valid url is there. Else hide the button (Just as mentioned above - for the case of TopBar). Also hide it when user is on Settings Page (As - not needed to do filter when viewing/inserting/updating configurations)
                (urls.includes(location.pathname.split("/")[1]) && location.pathname.split("/")[1] !== RoutesMapping["Settings"].url) && (location.pathname.split("/")[1] !== RoutesMapping["ExperimentPage"].url) ?
                <div>
                    <div className={styles.fab_search}>
                        <Zoom in={isExpanded}>
                            <Fab 
                                className={styles.fab_children}
                                variant="extended" 
                                onClick={() => {
                                    setFilterTextSearchDrawer(true);
                                    handleFabClick();
                                }}
                            >
                                <SearchIcon /> Text Search
                            </Fab>
                        </Zoom>
                    </div>

                    <div className={styles.fab_headers}>
                        <Zoom in={isExpanded}>
                            <Fab 
                                className={styles.fab_children}
                                variant="extended" 
                                onClick={() => {
                                    setFilterHeadersDrawer(true);
                                    handleFabClick();
                                }}
                        >
                                <DragHandleIcon /> Headers
                            </Fab>
                        </Zoom>
                    </div>

                    <div className={styles.fab_main}>
                        <Zoom in={true}>
                            <Fab 
                                color="primary" 
                                variant="extended" 
                                onClick={handleFabClick}
                            >
                                {
                                    isExpanded ?
                                    <ClearIcon/>
                                    :
                                    <FilterAltIcon/>
                                }
                                {
                                    isExpanded ?
                                    "Close"
                                    :
                                    "Filter"
                                }
                            </Fab>
                        </Zoom>
                    </div>
                </div>
                :
                null
            }
            <FilterTableHeaders 
                colNames={colNames}
                filterDrawer={filterHeadersDrawer} 
                setFilterDrawer={(filterDrawer: boolean)=>{
                    setFilterHeadersDrawer(filterDrawer);
                }}
            />
            <FilterTextSearch 
                colNames={colNames}
                filterDrawer={filterTextSearchDrawer} 
                setFilterDrawer={(filterDrawer: boolean)=>{
                    setFilterTextSearchDrawer(filterDrawer);
                }}
            />
        </div>
    );
}