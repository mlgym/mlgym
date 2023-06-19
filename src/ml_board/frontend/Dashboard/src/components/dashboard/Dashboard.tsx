import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { RoutesMapping } from '../../app/RoutesMapping';
import FilterProvider from './context/FilterContextProvider';
import FilterTableHeaders from './filterTableHeaders/FilterTableHeaders';
import FilterTextSearch from './filterTextSearch/FilterTextSearch';
import Table from "./table/Table";

// mui components & styles
import ClearIcon from '@mui/icons-material/Clear';
import DragHandleIcon from '@mui/icons-material/DragHandle';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import SearchIcon from '@mui/icons-material/Search';
import Fab from '@mui/material/Fab';
import Zoom from '@mui/material/Zoom';
import styles from './Dashboard.module.css';

export default function Dashboard() {

    const [filterHeadersDrawer, setFilterHeadersDrawer] = useState(false);
    const [filterTextSearchDrawer, setFilterTextSearchDrawer] = useState(false);

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
        <FilterProvider>
            <Table />
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
                                    {isExpanded ? <ClearIcon /> : <FilterAltIcon />}
                                    {isExpanded ? "Close" : "Filter"}
                                </Fab>
                            </Zoom>
                        </div>
                    </div>
                    :
                    null
            }
            <FilterTableHeaders
                filterDrawer={filterHeadersDrawer}
                setFilterDrawer={(filterDrawer: boolean) => {
                    setFilterHeadersDrawer(filterDrawer);
                }}
            />
            <FilterTextSearch
                filterDrawer={filterTextSearchDrawer}
                setFilterDrawer={(filterDrawer: boolean) => {
                    setFilterTextSearchDrawer(filterDrawer);
                }}
            />
        </FilterProvider>
    );
}