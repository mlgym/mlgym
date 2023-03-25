import { Toolbar } from '@mui/material';
import { CellClickedEvent, SelectionChangedEvent } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
// styles
import styles from './Table.module.css';

interface columnDefinition {
  field: string;
  sortable?: boolean;
  filter?: boolean
}


function Table({ colNames, rows }: { colNames: string[], rows: any[] }) {

  const navigate = useNavigate();
  
  // change the array of strings to array of colum definitions
  const colDefs: columnDefinition[] = colNames.map(
    (colName: string) => ({
      field: colName,
    })
  );

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

  // const onCellClicked = useCallback((event: CellClickedEvent) => { console.log(event) }, []);

  const onSelectionChanged = useCallback((event:SelectionChangedEvent) => {
    let selectedRowData = event.api.getSelectedRows()[0];
    navigate({
      pathname: '/experiment',
      search: '?experiment_id='+selectedRowData.experiment_id,
    })
  }, []);

  return (
    <div className="ag-theme-alpine" id={styles.ag_grid_container_table}>
      <Toolbar />
      <AgGridReact
        defaultColDef={defaultColDef}
        columnDefs={colDefs}
        rowData={rows}
        onGridReady={params => params.api.sizeColumnsToFit()}
        getRowId={(params: any) => params.data.job_id}
        animateRows={true}
        rowSelection={"single"}
        // onCellClicked={onCellClicked}
        onSelectionChanged={(event)=>onSelectionChanged(event)}
      >
      </AgGridReact>
    </div>
  )
}

export default Table;