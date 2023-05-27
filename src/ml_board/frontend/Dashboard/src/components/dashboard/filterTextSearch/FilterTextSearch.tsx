import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import TextField from '@mui/material/TextField';
import styles from './FilterTextSearch.module.css';
import { Button } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';

interface FilterTextSearchProps {
    colNames: Array<string>;
    filterDrawer: boolean;
    setFilterDrawer(filterDrawer:boolean): void;
}

const FilterTextSearch: React.FC<FilterTextSearchProps> = (props) => {

    const [filterText, setFilterText] = useState("");
    
    return(
        <React.Fragment>
            <Drawer
                anchor={"bottom"}
                open={props.filterDrawer}
                onClose={() => props.setFilterDrawer(false)}
                // Drawer wraps your content inside a <Paper /> component. A Materiaul-UI paper component has shadows and a non-transparent background.
                classes={{ paper: styles.textsearch_filter_drawer_container }}
            >
                <div>
                    <div className={styles.textsearch_filter_header_container}>
                        <h3 className={styles.textsearch_filter_header}>
                            Filter Your Results
                        </h3>
                    </div>
                    <div className={styles.textsearch_filter_textfield_container}>
                        <TextField
                            id="outlined-multiline-flexible"
                            label="Filter"
                            placeholder="Filter your experiments here!..."
                            multiline
                            maxRows={4}
                            value={filterText}
                            onChange={(e) => setFilterText(e.target.value)}
                            className={styles.textsearch_filter_textfield}
                        />
                    </div>
                    <div className={styles.textsearch_buttons_contianer}>
                        <Button 
                            className={styles.textsearch_button_save} 
                            variant="contained" 
                            startIcon={<CheckIcon />}
                        >
                            Save
                        </Button>
                        <Button 
                            className={styles.textsearch_button_cancel} 
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

export default FilterTextSearch;