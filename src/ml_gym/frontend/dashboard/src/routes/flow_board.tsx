import { AgGridReact } from "ag-grid-react";
import React from "react";
import { useAppSelector } from "../app/hooks"
import type { RootState } from '../app/store';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS

type FlowBoardProps = {
};


type JobStatusRowType = {
    job_id: number;
    job_type: string; //<CALC, TERMINATE>
    status: string; //<INIT, RUNNING, DONE>,
}


const jobStatusRowsSelector = (state: RootState) => state.jobStatus.map(s => (
    {
        job_id: s.data.payload.job_id,
        job_type: s.data.payload.job_type,
        status: s.data.payload.status,
        experiment_id: s.data.payload.experiment_id,
        starting_time: s.data.payload.starting_time,
        finishing_time: s.data.payload.finishing_time,
        error: s.data.payload.error,
        stacktrace: s.data.payload.stacktrace,
        device: s.data.payload.device,
    } as JobStatusRowType
)) //s.data.payload.job_id)


const FlowBoard: React.FC<FlowBoardProps> = ({ }) => {

    const jobStatusRows = useAppSelector(jobStatusRowsSelector)
    const colDefs = [
        { field: "job_id" },
        { field: "job_type" },
        { field: "status" },
        { field: "experiment_id" },
        { field: "starting_time" },
        { field: "finishing_time" },
        { field: "error" },
        { field: "stacktrace" },
        { field: "device" },
    ]

    return (
        <>
            <h1> Flow Board </h1>
            {/* <div>{jobIDs}</div> */}
            <div className="ag-theme-alpine"  style={{width: 1800, height: 800}}>
                <AgGridReact
                    // {/* provide column definitions */}
                    columnDefs={colDefs}
                    // {/* specify auto group column definition */}
                    // autoGroupColumnDef={this.autoGroupColumnDef}
                    // {/* row data provided via props from the file store */}
                    rowData={jobStatusRows}
                    // // enable tree data
                    // treeData={true}
                    // // {/* return tree hierarchy from supplied data */}
                    // getDataPath={data => data.filePath}
                    // // {/* expand tree by default */}
                    // groupDefaultExpanded={-1}
                    // // {/* fit grid columns */}
                    // onGridReady={params => params.api.sizeColumnsToFit()}
                    // // {/* provide context menu callback */}
                    // getContextMenuItems={this.getContextMenuItems}
                    // // {/* provide row drag end callback */}
                    // onRowDragEnd={this.onRowDragEnd}
                    // // {/* return id required for tree data and immutable data */}
                    // getRowId={params => params.data.id}
                    // // {/* specify our FileCellRenderer component */}
                    // components={this.components}
                    >
                </AgGridReact>
            </div>
        </>
    );
}

export default FlowBoard;