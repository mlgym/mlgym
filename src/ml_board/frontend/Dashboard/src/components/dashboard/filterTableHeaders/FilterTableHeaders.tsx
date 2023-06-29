import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';
import { Button, Checkbox, FormControlLabel, FormGroup } from '@mui/material';
import Drawer from '@mui/material/Drawer';
import React, { useContext, useEffect, useState } from 'react';
import { ColumnsFilter, FilterContext } from '../context/FilterContextProvider';
import styles from './FilterTableHeaders.module.css';

interface FilterTableHeaderProps {
    filterDrawer: boolean;
    setFilterDrawer(filterDrawer: boolean): void;
}

const FilterTableHeaders: React.FC<FilterTableHeaderProps> = (props) => {

    const { visibleColumns, setVisibleColumns } = useContext(FilterContext);
    const [localFilter, setLocalFilter] = useState<ColumnsFilter>(visibleColumns);

    useEffect(() => {
        setLocalFilter(visibleColumns);
    }, [visibleColumns]);

    return (
        <React.Fragment>
            <Drawer
                anchor={"right"}
                open={props.filterDrawer}
                onClose={() => props.setFilterDrawer(false)}
                // Drawer wraps your content inside a <Paper /> component. A Materiaul-UI paper component has shadows and a non-transparent background.
                classes={{ paper: styles.tableheader_filter_drawer_container }}
            >
                <div>
                    <div className={styles.tableheader_filter_header_container}>
                        <h3>
                            Filter Table Headers
                        </h3>
                    </div>
                    <div className={styles.tableheader_filter_checkbox_container}>
                        <FormGroup>
                            <div className={styles.tableheader_row_container}>
                                {
                                    Object.entries(visibleColumns).map(([colName, visible], index) => {
                                        return (
                                            <div className={styles.tableheader_string_item} key={index}>
                                                <FormControlLabel
                                                    control={
                                                        <Checkbox
                                                            onChange={(_, check) => {
                                                                setLocalFilter(prev => ({ ...prev, [colName]: check }));
                                                            }}
                                                            checked={localFilter[colName] ?? visible}
                                                        />}
                                                    label={colName} />
                                            </div>
                                        );
                                    })
                                }
                            </div>
                        </FormGroup>
                    </div>
                    <div className={styles.tableheader_buttons_contianer}>
                        <Button
                            className={styles.tableheader_button_save}
                            variant="contained"
                            startIcon={<CheckIcon />}
                            onClick={() => {
                                setVisibleColumns(localFilter);
                                props.setFilterDrawer(false);
                            }}
                        >
                            Save
                        </Button>
                        <Button
                            className={styles.tableheader_button_cancel}
                            variant="contained"
                            endIcon={<ClearIcon />}
                            onClick={() => props.setFilterDrawer(false)}
                        >
                            Cancel
                        </Button>
                    </div>
                </div>
            </Drawer>
        </React.Fragment>
    );
}

export default FilterTableHeaders;