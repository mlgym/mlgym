import React from 'react';
import Drawer from '@mui/material/Drawer';
import styles from './FilterTableHeaders.module.css';
import { Checkbox, FormControlLabel, FormGroup } from '@mui/material';
import { Button } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';

interface FilterTableHeaderProps {
    colNames: Array<string>;
    filterDrawer: boolean;
    setFilterDrawer(filterDrawer:boolean): void;
}

const FilterTableHeaders: React.FC<FilterTableHeaderProps> = (props) => {

    return(
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
                                props.colNames.map((colName, index) => {
                                    return(
                                        <div className={styles.tableheader_string_item} key={index}>
                                            <FormControlLabel control={<Checkbox />} label={colName} />
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