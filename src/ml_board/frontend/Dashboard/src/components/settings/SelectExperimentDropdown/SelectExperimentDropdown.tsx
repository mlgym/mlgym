import { getGridSearchId, getRestApiUrl } from '../../../redux/status/statusSlice';
import api from '../../../app/ApiMaster';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useAppSelector } from "../../../app/hooks";
import { Grid, Box, LinearProgress, Button } from '@mui/material';
import FormHelperText from '@mui/material/FormHelperText';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import SendIcon from '@mui/icons-material/Send';
import styles from './SelectExperimentDropdown.module.css';
import { useNavigate } from 'react-router-dom';
import { AnyKeyValuePairsInterface } from '../../experimentPage/ExperimentPage';

export default function SelectExperimentDropdown() {
    
    const [experimentIdsInDropdown, setExperimentIdsInDropdown] = useState(Array<string>);
    const [selectedExperiment, setSelectedExperiment] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);
    const navigate = useNavigate();

    useEffect(() => {

        setError("");
        setIsLoading(true);

        let experiments_url = api.experiments.replace("<grid_search_id>", grid_search_id);
        axios.get(rest_api_url + experiments_url).then((response) => {
            console.log("Got response from experiments API: ", response);
            if(response.status === 200) {
                if (response.data.length > 0) {
                    let experimentIdsInDropdown:Array<string> = [];
                    response.data.map((exp_data:AnyKeyValuePairsInterface ) => {
                        experimentIdsInDropdown.push(exp_data.experiment_id.toString());
                    });
                    experimentIdsInDropdown.sort();
                    setExperimentIdsInDropdown(experimentIdsInDropdown);
                    setSelectedExperiment(experimentIdsInDropdown[0]);
                }
                else {
                    setError("No Experiments Found!");
                }
            }
            else {
                setError("Oops! wrong file name / an error occurred");
            }
            setIsLoading(false);
        })
        .catch((error) => {
            console.log("Error in experiments API: ", error);
            setIsLoading(false);
            setError("Oops! wrong file name / an error occurred");
        });
    },[]);

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
        <div>
            <h2 className={styles.heading_style}>Experiment Details</h2>
            <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Box className={styles.textfield_cardcontent_select_experiment}>
                        <FormControl fullWidth={true} error={error.length > 0}>
                            <InputLabel id="demo-simple-select-helper-label">Experiment Id</InputLabel>
                            <Select
                                labelId="demo-simple-select-helper-label"
                                id="demo-simple-select-helper"
                                value={selectedExperiment}
                                label="Experiment Id"
                                onChange={(e)=>setSelectedExpValue(e.target.value)}
                                MenuProps={{ style: { maxHeight: "250px" } }} // have to keep style here. keeping it in css file is not working for this
                            >
                                {
                                    experimentIdsInDropdown.map((exp_id)=> 
                                        <MenuItem key={exp_id} value={exp_id}>{exp_id}</MenuItem>
                                    )
                                }
                            </Select>
                            {
                                error.length > 0 ?
                                <FormHelperText>
                                    {error}
                                </FormHelperText>
                                :
                                null
                            }
                        </FormControl>
                        <Button 
                            variant="contained" 
                            size="large" 
                            endIcon={<SendIcon />}
                            onClick={()=>goToSelectedExperiment()}
                            disabled={isLoading || error.length > 0}
                        >
                            
                        </Button>
                    </Box>
                </Grid>
                {
                    isLoading ?
                    <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                        <Box>
                            <LinearProgress />
                        </Box>
                    </Grid>
                    :
                    null
                }
            </Grid>
        </div>
    );
}