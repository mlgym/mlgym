import { Grid, Card, CardContent, TextField, IconButton, Switch, FormControlLabel, Box, LinearProgress } from '@mui/material';
import { Send, Download } from '@mui/icons-material';
import { JsonViewer } from '@textea/json-viewer';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api, { defaultExperimentConfigFileName } from '../../../../app/ApiMaster';
import { useAppSelector } from "../../../../app/hooks";
import { getGridSearchId, getRestApiUrl } from '../../../../redux/status/statusSlice';
import styles from './ExperimentConfigurations.module.css';

export default function ExperimentConfigurations({experimentIdProp} : {experimentIdProp: number}) {
    
    const [experimentConfigFileObject, setExperimentConfigFileObject] = useState({});
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showHideData, setShowHideData] = useState(false);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);

    useEffect(() => {
        if(experimentIdProp) {
            let experimentId = experimentIdProp.toString().trim();
            let experiment_config_file = api.experiment_config_file.replace("<grid_search_id>", grid_search_id);
            experiment_config_file = experiment_config_file.replace("<experiment_id>", experimentId);
            
            setError("");
            setShowHideData(false);
            setIsLoading(true);
    
            axios.get(rest_api_url + experiment_config_file).then((response) => {
                console.log("Got response from experiment_config API: ", response);
                if (response.status === 200) {
                    setExperimentConfigFileObject(response.data);
                    setShowHideData(true);
                }
                else {
                    setError("Oops! wrong experiment id / file name / an error occurred");
                }
                setIsLoading(false);
            })
            .catch((error) => {
                console.log("Error in experiment_config_file: ", error);
                setIsLoading(false);
                setError("Oops! wrong file name / an error occurred");
            });
        }
    },[experimentIdProp]);

    function downloadFile() {
        if(experimentIdProp) {
            let experimentId = experimentIdProp.toString().trim();
            const dataStr = JSON.stringify(experimentConfigFileObject, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            const linkElement = document.createElement("a");
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', defaultExperimentConfigFileName.trim()+"_experiment_"+experimentId+".json");
            linkElement.click();
        }
    }

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <Box className={styles.textfield_cardcontent_experiment_config}>
                    <h2 className={styles.heading_style}>Experiment Configuration File</h2>
                    <div>
                        {
                            !isLoading && error.length === 0 && Object.keys(experimentConfigFileObject).length > 0 ?
                            <IconButton 
                                size="large"
                                onClick={()=>downloadFile()}
                            >
                                <Download /> 
                            </IconButton>
                            :
                            null
                        }
                        {
                            !isLoading && error.length === 0 && Object.keys(experimentConfigFileObject).length > 0 ?
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
                    </div>
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
            {
                !isLoading && error.length === 0 && Object.keys(experimentConfigFileObject).length > 0 && showHideData ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Card>
                        <CardContent>
                            <JsonViewer value={experimentConfigFileObject}/>
                        </CardContent>
                    </Card>
                </Grid>
                :
                !isLoading && error.length !== 0 ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Box className={styles.error_text}>
                        Error Occured In Getting Experiment Configuration File!
                    </Box>
                </Grid>
                :
                null
            }
        </Grid>
    );
}