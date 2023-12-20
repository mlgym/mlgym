import { ColDef, GetRowIdFunc, GetRowIdParams, GridColumnsChangedEvent, GridReadyEvent, ICellRendererParams, RowClassParams, RowStyle } from 'ag-grid-community';
import { AgGridReact } from "ag-grid-react";
import { useCallback, useContext, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../../app/hooks';
import { Row, selectAllRows, selectTableHeaders } from '../../../redux/table/tableSlice';

// components & styles
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { IconButton, Tooltip } from '@mui/material';
import 'ag-grid-community/styles/ag-grid.css'; // Core grid CSS, always needed
import 'ag-grid-community/styles/ag-theme-alpine.css'; // Optional theme CSS
import styles from './Table.module.css';

// TODO: Maybe merge Table and Dashboard?
export default function Table() {

  const navigate = useNavigate();

  const rows = useAppSelector(selectAllRows);
  const headers = useAppSelector(selectTableHeaders);

  // map the visible columns obejct to an array, every element on the format { field: colName }, only taking the visible ones
  const colDefs: ColDef<Row>[] = useMemo(() => {
    const arr: ColDef<Row>[] = Object.entries(headers).reduce((keys: ColDef<Row>[], [colName, visible]) => {
      if (visible === true) {
        keys.push({ field: colName });
      }
      return keys;
    }, [{
      pinned: "right", minWidth: 50, maxWidth: 50,
      resizable: false, sortable: false, filter: false,
      cellRenderer: (params: ICellRendererParams) => (
        <Tooltip title="Go to the Experiment Page" arrow placement='top-start'>
          <IconButton
            size="small"
            onClick={() => {
              navigate({
                pathname: '/experiment',
                search: '?experiment_id=' + (params.data as Row).experiment_id.toString(),
              })
            }}
          >
            <OpenInNewIcon />
          </IconButton>
        </Tooltip>)
    }]);
    return arr;
  }, [headers]);

  const defaultColDef = useMemo(() => ({ resizable: true, sortable: true, filter: true }), []);

  const onGridColumnsChanged: (params: GridColumnsChangedEvent<Row>) => void = useCallback(params => params.api.sizeColumnsToFit(), []);
  const getRowId: GetRowIdFunc<Row> = useCallback((params: GetRowIdParams<Row>) => params.data.experiment_id.toString(), []);

  // set background colour for every row based on the rowIndex, as it is the same as experiment_id. BUT this looks bad, should be using CSS classes?
  const getRowStyle = ({ rowIndex }: RowClassParams): RowStyle => { return { background: `hsl(${rowIndex * 137.5},75%,50%)` }; };

  return (
    <div className="ag-theme-alpine" id={styles.ag_grid_container_table}>
      {/* NOTE: https://www.ag-grid.com/react-data-grid/row-styles/ */}
      <AgGridReact
        defaultColDef={defaultColDef}
        columnDefs={colDefs}
        rowData={rows}
        onGridColumnsChanged={onGridColumnsChanged}
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