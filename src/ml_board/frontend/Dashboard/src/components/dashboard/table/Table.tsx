import { ColDef, GetRowIdFunc, GetRowIdParams, GridReadyEvent, RowDoubleClickedEvent } from 'ag-grid-community';
import { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row } from '../../../redux/table/tableSlice';
// styles
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import styles from './Table.module.css';

// TODO: Maybe merge Table and Dashboard?
export default function Table({ colNames, rows }: { colNames: string[], rows: any[] }) {

  const navigate = useNavigate();

  // change the array of strings to array of colum definitions
  const colDefs: ColDef<Row>[] = useMemo(() => colNames.map(
    (colName: string) => ({
      field: colName,
    })
  ), [colNames]);

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

  const onRowClicked = useCallback((event: RowDoubleClickedEvent) => {
    const selectedRowData = event.api.getSelectedRows()[0];
    navigate({
      pathname: '/experiment',
      search: '?experiment_id=' + selectedRowData.experiment_id,
    })
  }, []);

  // set background colour for every row based on the rowIndex, as it is the same as experiment_id. BUT this looks bad, should be using CSS classes?
  // const getRowStyle = ({ rowIndex }: RowClassParams): RowStyle => { return { background: `hsl(${rowIndex * 137.5},75%,50%)` }; };
  const onGridReady: (params: GridReadyEvent<Row>) => void = useCallback(params => params.api.sizeColumnsToFit(), []);
  const getRowId: GetRowIdFunc<Row> = useCallback((params: GetRowIdParams<Row>) => params.data.experiment_id.toString(), []);

  return (
    <div className="ag-theme-alpine" id={styles.ag_grid_container_table}>
      {/* NOTE: https://www.ag-grid.com/react-data-grid/row-styles/ */}
      <AgGridReact
        defaultColDef={defaultColDef}
        columnDefs={colDefs}
        rowData={rows}
        onGridReady={onGridReady}
        getRowId={getRowId}
        rowSelection={"multiple"}
        onRowClicked={onRowClicked}
        rowStyle={{ cursor: "pointer" }}
        animateRows={true} // Optional - set to 'true' to have rows animate when sorted
        enableCellChangeFlash={true}
      >
      </AgGridReact>
    </div>
  )
}