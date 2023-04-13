import { Grid, Card, CardContent, TextField, IconButton, Switch, FormControlLabel, Box, LinearProgress } from '@mui/material';
import { Send, Download } from '@mui/icons-material';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api from '../../../../app/ApiMaster';
import { useAppSelector } from "../../../../app/hooks";
import { getGridSearchId, getRestApiUrl } from '../../../../redux/status/statusSlice';
import styles from './CheckpointConfigurations.module.css';

const defaultCheckpointIdHelperText = "eg: 1";
interface CheckpointDataInterface {
    [key: string]: Blob
}
var checkpointDataObj: CheckpointDataInterface = {}

export default function CheckpointConfigurations({experimentIdProp} : {experimentIdProp: number}) {

    const [experimentId, setExperimentId] = useState("");
    const [checkpointId, setCheckpointId] = useState("");
    const [checkpointData, setCheckpointData] = useState(checkpointDataObj);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showHideData, setShowHideData] = useState(false);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);

    useEffect(() => {
        if(experimentIdProp) {
            setExperimentId(experimentIdProp.toString());
        }
    },[experimentIdProp]);

    function changeText(text:string) {
        setError("");
        setShowHideData(false);
        setCheckpointData(checkpointDataObj);
        setCheckpointId(text);
    }
    
    function get_experiment_config_file() {
        
        let checkpoint_url = api.checkpoint_url.replace("<grid_search_id>", grid_search_id);
        checkpoint_url = checkpoint_url.replace("<experiment_id>", experimentId.trim().toString());
        checkpoint_url = checkpoint_url.replace("<checkpoint_id>", checkpointId.trim().toString());
        
        setError("");
        setShowHideData(false);
        setIsLoading(true);

        axios.get(rest_api_url + checkpoint_url).then((response) => {
            console.log("Got response from get_checkpoint API: ", response);
            if (response.status === 200) {
                let resp_data = response.data;
                if (Object.keys(resp_data).length === 0) {
                    setError("No data available!");
                }
                else {
                    Object.keys(resp_data).map((resourceName) => {
                        checkpointData[resourceName] = resp_data[resourceName];
                    });
                    setCheckpointData(checkpointData);
                    setShowHideData(true);
                }
            }
            else {
                setError("Oops! wrong checkpoint id / an error occurred");
            }
            setIsLoading(false);
        })
        .catch((error) => {
            console.log("Error in get_checkpoint: ", error);
            setIsLoading(false);
            setError("Oops! wrong checkpoint id / an error occurred");
        });
    }

    function downloadFile(resourceName: string) {
        let fileData = checkpointData[resourceName];
        const url = window.URL.createObjectURL(fileData!);
        const a = document.createElement('a');
        a.href = url;
        a.download = "checkpoint"+checkpointId.trim().toString()+"_experiemnt_"+experimentId.trim().toString();
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <Card>
                    <CardContent className={styles.textfield_cardcontent_checkpoint_config}>
                        <TextField
                            id="outlined-multiline-flexible"
                            fullWidth={true}
                            label="Enter Checkpoint Id"
                            error={error.length > 0}
                            helperText={error.length > 0? error : defaultCheckpointIdHelperText}
                            value={checkpointId}
                            disabled={isLoading}
                            onChange={(e)=>changeText(e.target.value)}
                        />
                        <IconButton 
                            size="large" 
                            disabled={isLoading || checkpointId.length === 0}
                            onClick={()=>get_experiment_config_file()}
                        >
                            <Send /> 
                        </IconButton>
                        {
                            !isLoading && error.length === 0 && Object.keys(checkpointData).length > 0 ?
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={showHideData}
                                        color="primary"
                                        onChange={()=>setShowHideData(!showHideData)}
                                    />
                                }
                                label={"View/Hide"}
                            />
                            :
                            null
                        }
                    </CardContent>
                </Card>
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
            {
                !isLoading && error.length === 0 && Object.keys(checkpointData).length > 0 && showHideData ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Card>
                        <CardContent>
                            {
                                Object.keys(checkpointData).map((resourceName) => {
                                    return(
                                        <Box className={styles.checkpoint_data_resources}>
                                            <div>
                                                {resourceName}
                                            </div>
                                            <IconButton 
                                                size="large"
                                                onClick={()=>downloadFile(resourceName)}
                                            >
                                                <Download /> 
                                            </IconButton>
                                        </Box>
                                    );
                                })
                            }
                        </CardContent>
                    </Card>
                </Grid>
                :
                null
            }
        </Grid>
    );
}