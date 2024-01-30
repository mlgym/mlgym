import React, { useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import { ColumnsFilter, selectTableHeaders, updateTableHeaderVisibility } from '../../../redux/table/tableSlice';

// components & styles
import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';
import { Button } from '@mui/material';
import Drawer from '@mui/material/Drawer';
import TextField from '@mui/material/TextField';
import styles from './FilterTextSearch.module.css';


const TEXT_FILTER_SEPARATOR = ";";

interface FilterTextSearchProps {
    filterDrawer: boolean;
    setFilterDrawer(filterDrawer: boolean): void;
}

const FilterTextSearch: React.FC<FilterTextSearchProps> = (props) => {

    const dispatch = useAppDispatch();
    const headers = useAppSelector(selectTableHeaders);

    const text = useRef<{ value: string }>();

    function processFilter(input: string) {
        const temp: ColumnsFilter = {}
        for (const inputChunk of input.split(TEXT_FILTER_SEPARATOR)) {
            const re = new RegExp(inputChunk);
            for (const header in headers) {
                if (!temp[header])
                    temp[header] = re.test(header)
            }
        }
        dispatch(updateTableHeaderVisibility(temp));
    }

    return (
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
                            autoFocus={true}
                            inputRef={text}
                            id="outlined-multiline-flexible"
                            label="Filter"
                            placeholder="Filter your experiments here!..."
                            multiline
                            maxRows={4}
                            className={styles.textsearch_filter_textfield}
                        />
                    </div>
                    <div className={styles.textsearch_buttons_contianer}>
                        <Button
                            className={styles.textsearch_button_save}
                            variant="contained"
                            startIcon={<CheckIcon />}
                            onClick={() => {
                                processFilter(text.current?.value!)
                                props.setFilterDrawer(false)
                            }}
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