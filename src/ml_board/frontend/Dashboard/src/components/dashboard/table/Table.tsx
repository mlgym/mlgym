import { RowDoubleClickedEvent } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
// styles
import styles from './Table.module.css';

interface columnDefinition { field: string; }

// TODO: Maybe merge Table and Dashboard?
export default function Table({ colNames, rows }: { colNames: string[], rows: any[] }) {

  const navigate = useNavigate();

  // change the array of strings to array of colum definitions
  const colDefs: columnDefinition[] = colNames.map(
    (colName: string) => ({
      field: colName,
    })
  );

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

  const onRowDoubleClicked = useCallback((event: RowDoubleClickedEvent) => {
    const selectedRowData = event.api.getSelectedRows()[0];
    navigate({
      pathname: '/experiment',
      search: '?experiment_id=' + selectedRowData.experiment_id,
    })
  }, []);

  // set background colour for every row based on the rowIndex, as it is the same as experiment_id. BUT this looks bad, should be using CSS classes?
  // const getRowStyle = ({ rowIndex }: RowClassParams): RowStyle => { return { background: `hsl(${rowIndex * 137.5},75%,50%)` }; };

  return (
    <div className="ag-theme-alpine" id={styles.ag_grid_container_table}>
      {/* NOTE: https://www.ag-grid.com/react-data-grid/row-styles/ */}
      <AgGridReact
        defaultColDef={defaultColDef}
        columnDefs={colDefs}
        rowData={rows}
        onGridReady={params => params.api.sizeColumnsToFit()}
        getRowId={(params: any) => params.data.job_id}
        rowSelection={"multiple"}
        onRowDoubleClicked={onRowDoubleClicked}
        rowStyle={{ cursor: "pointer" }}
        animateRows={true} // Optional - set to 'true' to have rows animate when sorted
      >
      </AgGridReact>
    </div>
  )
}