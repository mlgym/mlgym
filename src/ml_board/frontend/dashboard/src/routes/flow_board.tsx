import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import { AgGridReact } from "ag-grid-react";
import React from "react";
import { connect } from "react-redux";
import type { RootState } from '../app/store';
import { jobStatusRowsSelector } from '../features/jobsStatus/jobsStatusSlice';

import { JobStatusRowType, ModelEvaluationRowType, ModelStatusRowType } from '../app/datatypes';
import { useAppSelector } from '../app/hooks';

type FlowBoardPropsType = {
    jobStatusRows: any
};



const statusRowsSelector = (state: RootState) => {
    const jobStatusRows = jobStatusRowsSelector(state)

    const fullRows = jobStatusRows.map((jobStatusRow: JobStatusRowType) => {
        const latest_message_index = state.modelsStatus.experiment_id_to_latest_message_index[jobStatusRow.experiment_id]
        const latest_message_index2 = state.modelsEvaluation.experiment_id_to_latest_message_index[jobStatusRow.experiment_id]
        var returnValue = jobStatusRow;

        if (!(latest_message_index === undefined)) {
            const modelStatusMessage = state.modelsStatus.messages[latest_message_index].data.payload
            const modelStatusRow = {
                experiment_id: modelStatusMessage.experiment_id,
                model_status: modelStatusMessage.status,
                num_epochs: modelStatusMessage.num_epochs,
                current_epoch: modelStatusMessage.current_epoch,
                splits: modelStatusMessage.splits,
                current_split: modelStatusMessage.current_split,
                epoch_progress: modelStatusMessage.current_epoch / modelStatusMessage.num_epochs,
                batch_progress: modelStatusMessage.current_batch / modelStatusMessage.num_batches,
            } as ModelStatusRowType

            returnValue = { ...returnValue, ...modelStatusRow }
        }

        if (!(latest_message_index2 === undefined)) {
            const modelEvaluationMsg = state.modelsEvaluation.messages[latest_message_index].data.payload
            const modelEvaluationRow = {
                f1_score_macro: modelEvaluationMsg.metric_scores[0].score,
                precision_macro: modelEvaluationMsg.metric_scores[1].score,
                recall_macro: modelEvaluationMsg.metric_scores[2].score,
            } as ModelEvaluationRowType

            returnValue = { ...returnValue, ...modelEvaluationRow }
        }

        return returnValue;
    });

    return fullRows
}



const FlowBoard: React.FC<FlowBoardPropsType> = (jobStatusRows: any) => {

    // class FlowBoard extends Component<FlowBoardPropsType> {
    //     render() {
    //const jobStatusRows = useAppSelector(statusRowsSelector)

    const colNames = ["job_id", "job_type", "job_status", "experiment_id", "starting_time", "finishing_time",
        "epoch_progress", "batch_progress", "model_status", "current_split", "splits", "error",
        "stacktrace", "device", "current_epoch", "num_epochs", "f1_score_macro", "precision_macro", "recall_macro"]


    const re = new RegExp(useAppSelector((state: RootState) => state.RegEx.value))

    const colDefs = colNames.filter(
        (colName: string) => re.test(colName)
    ).map(
        (colName: string) => ({ field: colName })
    )



    return (
        <>
            {/* <h1> Flow Board </h1> */}
            <div className="ag-theme-alpine" id="ag-grid-container">
                <AgGridReact
                    defaultColDef={{ resizable: true }}
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