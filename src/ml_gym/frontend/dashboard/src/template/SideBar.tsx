import React from "react";
import "./SideBar.css";
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import TuneIcon from '@mui/icons-material/Tune';
import ModelTrainingIcon from '@mui/icons-material/ModelTraining';
import CellTowerIcon from '@mui/icons-material/CellTower';
import { Link } from 'react-router-dom';
import ExpandCollapseButton from "./ExpandCollapseButton";

type SideBarPropsType = {
    children?: React.ReactNode;
    sideBarExpanded: boolean;
    toggleSidebar: () => void;
    setSelectedPageId: (page_id: number) => void;
    selectedPageId: number
};

const SideBar: React.FC<SideBarPropsType> = ({ toggleSidebar, sideBarExpanded, setSelectedPageId, selectedPageId }) => {
    return (
        <div className={"left-navbar " + (sideBarExpanded && "show") }>
            <nav className={"nav_list nav " + (sideBarExpanded && "show")}>
                <a href="#" className="nav_logo"> <i className='bx bx-layer nav_logo-icon'></i>  <span className="nav_logo-name">MLgym</span>  </a>
                <Link to="/flowboard" className={(selectedPageId === 0) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(0) }}>
                    <ModelTrainingIcon /> <span className="nav_name">Flow Board</span>
                </Link>
                <Link to="/analysisboard" className={(selectedPageId === 1) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(1) }}>
                    <StackedLineChartIcon /> <span className="nav_name">Analysis Board</span>
                </Link>
                <Link to="/throughput" className={(selectedPageId === 2) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(2) }}>
                    <CellTowerIcon /> <span className="nav_name">Throughput Board</span>
                </Link>
                <Link to="/settings" className={(selectedPageId === 3) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(3) }}>
                    <TuneIcon /> <span className="nav_name">Settings</span>
                </Link>
                <ExpandCollapseButton sideBarExpanded={sideBarExpanded} toggleSidebar={toggleSidebar} />
            </nav >
        </div >
    );
}


export default SideBar;

