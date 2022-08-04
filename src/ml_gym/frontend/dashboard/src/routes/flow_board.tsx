import { AgGridReact } from "ag-grid-react";
import React, { Component } from "react";
import type { RootState } from '../app/store';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import { jobStatusRowsSelector } from '../features/jobsStatus/jobsStatusSlice'
import { connect } from "react-redux";

import { JobStatusRowType, ModelStatusRowType } from '../app/datatypes'

type FlowBoardPropsType = {
    jobStatusRows: any
};



const statusRowsSelector = (state: RootState) => {
    const jobStatusRows = jobStatusRowsSelector(state)

    const fullRows = jobStatusRows.map((jobStatusRow: JobStatusRowType) => {
        const latest_message_index = state.modelsStatus.experiment_id_to_latest_message_index[jobStatusRow.experiment_id]
        if (latest_message_index) {
            const modelStatusMessage = state.modelsStatus.messages[latest_message_index]
            const modelStatusRow = {
                experiment_id: modelStatusMessage.data.payload.experiment_id,
                model_status: modelStatusMessage.data.payload.status,
                num_epochs: modelStatusMessage.data.payload.num_epochs,
                current_epoch: modelStatusMessage.data.payload.current_epoch,
                splits: modelStatusMessage.data.payload.splits,
                current_split: modelStatusMessage.data.payload.current_split,
                epoch_progress: modelStatusMessage.data.payload.current_epoch / modelStatusMessage.data.payload.num_epochs,
                batch_progress: modelStatusMessage.data.payload.current_batch / modelStatusMessage.data.payload.num_batches,
            } as ModelStatusRowType


            return { ...jobStatusRow, ...modelStatusRow }
        } else {
            return jobStatusRow
        }
    });

    return fullRows
}



const FlowBoard: React.FC<FlowBoardPropsType> = (jobStatusRows: any) => {

    // class FlowBoard extends Component<FlowBoardPropsType> {
    //     render() {
    //const jobStatusRows = useAppSelector(statusRowsSelector)


    const colDefs = [
        { field: "job_id" },
        { field: "job_type" },
        { field: "job_status" },
        { field: "experiment_id" },
        { field: "starting_time" },
        { field: "finishing_time" },
        { field: "epoch_progress" },
        { field: "batch_progress" },
        { field: "model_status" },
        { field: "current_split" },
        { field: "splits" },
        { field: "error" },
        { field: "stacktrace" },
        { field: "device" },

    ]

    return (
        <>
            {/* <h1> Flow Board </h1> */}
            <div className="ag-theme-alpine" id="ag-grid-container">
                <AgGridReact
                    // {/* provide column definitions */}
                    columnDefs={colDefs}
                    // {/* specify auto group column definition */}
                    // autoGroupColumnDef={this.autoGroupColumnDef}
                    // {/* row data provided via props from the file store */}
                    rowData={jobStatusRows.jobStatusRows}
                    // // enable tree data
                    // treeData={true}
                    // // {/* return tree hierarchy from supplied data */}
                    // getDataPath={data => data.filePath}
                    // // {/* expand tree by default */}
                    // groupDefaultExpanded={-1}
                    // // {/* fit grid columns */}
                    onGridReady={params => params.api.sizeColumnsToFit()}
                    // // {/* provide context menu callback */}
                    // getContextMenuItems={this.getContextMenuItems}
                    // // {/* provide row drag end callback */}
                    // onRowDragEnd={this.onRowDragEnd}
                    // // {/* return id required for tree data and immutable data */}
                    getRowId={(params: any) => params.data.job_id}
                    // // {/* specify our FileCellRenderer component */}
                    // components={this.components}
                    animateRows={true} // Optional - set to 'true' to have rows animate when sorted

                >
                </AgGridReact>
            </div>
        </>
    );
}
// }

const mapStateToProps = (state: RootState) => {
    return { "jobStatusRows": statusRowsSelector(state) }
};

const mapDispatchToProps = (appDispatch: any) => ({
    actions: {}
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
    null,
    { forwardRef: true } // must be supplied for react/redux when using AgGridReact
)(FlowBoard);