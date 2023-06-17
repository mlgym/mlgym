import { ColDef, GetRowIdFunc, GetRowIdParams, GridReadyEvent, ICellRendererParams } from 'ag-grid-community';
import { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row } from '../../../redux/table/tableSlice';
// styles
import SendIcon from '@mui/icons-material/Send';
import { IconButton } from '@mui/material';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import styles from './Table.module.css';

// TODO: Maybe merge Table and Dashboard?
export default function Table({ colNames, rows }: { colNames: string[], rows: any[] }) {

  const navigate = useNavigate();

  // change the array of strings to array of colum definitions
  const colDefs: ColDef<Row>[] = useMemo(() => {
    const arr: ColDef<Row>[] = colNames.map((colName: string) => ({ field: colName }));
    arr.push({
      pinned: "left", minWidth: 50, maxWidth: 50, 
      resizable: false, sortable: false, filter: false,
       cellRenderer: (params: ICellRendererParams) => (
        <IconButton
          size="small"
          onClick={() => {
            navigate({
              pathname: '/experiment',
              search: '?experiment_id=' + (params.data as Row).experiment_id.toString(),
            })
          }}
        >
          <SendIcon />
        </IconButton>)
    });
    return arr;
  }, [colNames]);

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

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
        rowStyle={{ cursor: "pointer" }}
        animateRows={true} // Optional - set to 'true' to have rows animate when sorted
        enableCellChangeFlash={true}
      >
      </AgGridReact>
    </div>
  )
}