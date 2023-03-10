import { Toolbar } from '@mui/material';
import { CellClickedEvent } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo } from 'react';
// styles
import './Table.scss';


interface columnDefinition {
  field: string;
}

// TODO: Maybe merge table and Dashboard?
function Table({ colNames, rows }: { colNames: string[], rows: any[] }) {

  // change the array of strings to array of colum definitions
  const colDefs: columnDefinition[] = colNames.map(
    (colName: string) => ({
      field: colName,
    })
  );

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

  const onCellClicked = useCallback((event: CellClickedEvent) => { console.log(event) }, []);

  return (
    <div className="ag-theme-alpine" id="ag-grid-container">
      <Toolbar />
      <AgGridReact
        defaultColDef={defaultColDef}
        // {/* provide column definitions */}
        columnDefs={colDefs}
        // {/* specify auto group column definition */}
        // autoGroupColumnDef={this.autoGroupColumnDef}
        // {/* row data provided via props from the file store */}
        rowData={rows}
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
        rowSelection="multiple"
        onCellClicked={onCellClicked}
      >
      </AgGridReact>
    </div>
  )
}

export default Table;