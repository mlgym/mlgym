import React from "react";
import "./ExpandCollapseButton.css";
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';

type ExpandCollapseButtonPropsType = {
    sideBarExpanded: boolean;
    toggleSidebar: () => void;
};


const ExpandCollapseButton: React.FC<ExpandCollapseButtonPropsType> = ({ sideBarExpanded, toggleSidebar }) => {
    if (sideBarExpanded) {
        return (<div className="nav_link expand-collapse-button"><KeyboardDoubleArrowLeftIcon onClick={toggleSidebar} /></div>);
    } else {
        return (<div className="nav_link expand-collapse-button"><KeyboardDoubleArrowRightIcon onClick={toggleSidebar} /></div>);
    }
};

export default ExpandCollapseButton;

