import React, { useState } from "react";
import "./template.css";
import GlobalConfig from "../features/globalConfig/globalConfig";
import SideBar from "./SideBar";
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



const Template: React.FC<TemplatePropsType> = ({ toggleSidebar, sideBarExpanded, setSelectedPageId, selectedPageId, filterConfig, setFilterConfig, children }) => {

    const [size, setSize] = useState("0px");
    function ConfigResized(size: string) {
        setSize(size)
    }

    return (
        <>
            <SideBar toggleSidebar={toggleSidebar} sideBarExpanded={sideBarExpanded} setSelectedPageId={setSelectedPageId} selectedPageId={selectedPageId} />

            <div className="flex-container">
                <div className="children-content" style={{ height: `calc(100vh - ${size})` }}>
                    {children}
                </div>
                <GlobalConfig filterConfig={filterConfig} setFilterConfig={setFilterConfig} ConfigResized={ConfigResized} />
            </div>
        </>

    );
};

export default Template;

