import React from "react";
import "./template.css";
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import TuneIcon from '@mui/icons-material/Tune';
import ModelTrainingIcon from '@mui/icons-material/ModelTraining';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';
import CellTowerIcon from '@mui/icons-material/CellTower';
import { Link } from 'react-router-dom';
import GlobalConfig from "../features/globalConfig/globalConfig";
import { FilterConfigType } from "../app/datatypes"

type TemplatePropsType = {
    children?: React.ReactNode;
    sideBarExpanded: boolean;
    toggleSidebar: () => void;
    setSelectedPageId: (page_id: number) => void;
    selectedPageId: number
    filterConfig: FilterConfigType
    setFilterConfig: (filterConfig: FilterConfigType) => void
};

type SideBarPropsType = {
    children?: React.ReactNode;
    sideBarExpanded: boolean;
    toggleSidebar: () => void;
    setSelectedPageId: (page_id: number) => void;
    selectedPageId: number
};

type ExpandCollapseButtonPropsType = {
    sideBarExpanded: boolean;
    toggleSidebar: () => void;
};


const ExpandCollapseButton: React.FC<ExpandCollapseButtonPropsType> = ({ sideBarExpanded, toggleSidebar }) => {
    if (sideBarExpanded) {
        return (<div className="nav_link expand-collapse-button"><KeyboardDoubleArrowLeftIcon className="expand-collapse-button" onClick={toggleSidebar} /></div>);
    } else {
        return (<div className="nav_link expand-collapse-button"><KeyboardDoubleArrowRightIcon onClick={toggleSidebar} /></div>);
    }
};



const SideBar: React.FC<SideBarPropsType> = ({ toggleSidebar, sideBarExpanded, setSelectedPageId, selectedPageId }) => {
    return (
        <div id="body-pd" className="body-pd">

            <div className={sideBarExpanded ? "l-navbar show" : "l-navbar"} id="nav-bar">
                <nav className={sideBarExpanded ? "nav show" : "nav"}>
                    <div>
                        <a href="#" className="nav_logo"> <i className='bx bx-layer nav_logo-icon'></i>  <span className="nav_logo-name">MLgym</span>  </a>
                        <div className="nav_list">
                            <Link to="/flowboard" className={(selectedPageId == 0) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(0) }}>
                                <ModelTrainingIcon /> <span className="nav_name">Flow Board</span>
                            </Link>
                            <Link to="/analysisboard" className={(selectedPageId == 1) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(1) }}>
                                <StackedLineChartIcon /> <span className="nav_name">Analysis Board</span>
                            </Link>
                            <Link to="/throughput" className={(selectedPageId == 2) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(2) }}>
                                <CellTowerIcon /> <span className="nav_name">Throughput Board</span>
                            </Link>
                            <Link to="/settings" className={(selectedPageId == 3) ? "nav_link active" : "nav_link"} onClick={() => { setSelectedPageId(3) }}>
                                <TuneIcon /> <span className="nav_name">Settings</span>
                            </Link>
                            <ExpandCollapseButton sideBarExpanded={sideBarExpanded} toggleSidebar={toggleSidebar} />
                        </div>
                    </div>
                </nav >
            </div >
        </div >
    );
}


const Template: React.FC<TemplatePropsType> = ({ toggleSidebar, sideBarExpanded, setSelectedPageId, selectedPageId, filterConfig, setFilterConfig, children }) => (
    <>
        <div className="styles.body">
            <SideBar toggleSidebar={toggleSidebar} sideBarExpanded={sideBarExpanded} setSelectedPageId={setSelectedPageId} selectedPageId={selectedPageId} />
            <div className="children-content">
                {children}
            </div>
            <GlobalConfig filterConfig={filterConfig} setFilterConfig={setFilterConfig} />
        </div>
    </>

);

export default Template;

