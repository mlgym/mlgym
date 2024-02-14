import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../../app/hooks';
import { selectExperimentsPerChartById } from '../../../redux/charts/chartsSlice';
// components & styles
import SendIcon from '@mui/icons-material/Send';
import { Box, IconButton } from '@mui/material';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import styles from "./SelectExperimentDropdown.module.css";

export default function SelectExperimentDropdown({chart_id} : {chart_id:string}) {
    
    // TODO: this selector is causing the FC to be rerendered multiple times
    // first: understand why this is the case?!
    // second: maybe use createSelector from Reselect (https://redux.js.org/usage/deriving-data-selectors#createselector-overview)
    const experimentsDict = useAppSelector(state => selectExperimentsPerChartById(state, chart_id));
    const [selectedExperiment, setSelectedExperiment] = useState("");
    const navigate = useNavigate();
    
    function goToSelectedExperiment() {
        if (selectedExperiment !== "") {
            navigate({
                pathname: '/experiment',
                search: '?experiment_id='+selectedExperiment,
            });
        }
    }

    function setSelectedExpValue(value: string) {
        setSelectedExperiment(value);
    }

    return(
        <Box className={styles.selection_to_exp_page}>
            <div className={styles.selection_to_exp_page_text}>
                Take me to experiment page: 
            </div>
            <FormControl variant="standard" fullWidth={true} className={styles.selection_to_exp_page_form_control}>
                <InputLabel id="demo-simple-select-standard-label">Experiment Id</InputLabel>
                <Select
                    labelId="demo-simple-select-standard-label"
                    id="demo-simple-select-standard"
                    value={selectedExperiment}
                    label="Experiment Id"
                    onChange={(e)=>setSelectedExpValue(e.target.value)}
                    MenuProps={{ style: { maxHeight: "200px" } }} // have to keep style here. keeping it in css file is not working for this
                >
                    {
                        Object.values(experimentsDict).map((exp)=> 
                            <MenuItem key={exp!.exp_id} value={exp!.exp_id}>{exp!.exp_id}</MenuItem>
                        )
                    }
                </Select>
            </FormControl>
            <IconButton 
                size="large"
                onClick={()=>goToSelectedExperiment()}
                disabled={selectedExperiment===""}
            >
                <SendIcon />
            </IconButton>
        </Box>
    );
}