import { useState } from 'react';
import { IconButton, Box} from '@mui/material';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import SendIcon from '@mui/icons-material/Send';
import { useNavigate } from 'react-router-dom';
import { selectExperimentsPerChartById } from '../../../redux/charts/chartsSlice';
import { useAppSelector } from '../../../app/hooks';
import styles from "./SelectExperimentDropdown.module.css";

export default function SelectExperimentDropdown({chart_id} : {chart_id:string}) {
    
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