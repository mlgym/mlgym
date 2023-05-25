import { Grid, Card, CardContent, IconButton, Switch, FormControlLabel, Box, LinearProgress } from '@mui/material';
import { Download } from '@mui/icons-material';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api, { defaultGridSearchConfigFileName } from '../../../app/ApiMaster';
import { useAppSelector } from "../../../app/hooks";
import { getGridSearchId, getRestApiUrl, getSocketConnectionUrl, isConnected } from '../../../redux/status/statusSlice';
import styles from './GridSearchConfigurations.module.css';

export default function GridSearchConfigurations() {
    
    const isSocketConnected = useAppSelector(isConnected);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);
    const socket_connection_url = useAppSelector(getSocketConnectionUrl);
    
    const [yamlString, setYamlString] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showHideData, setShowHideData] = useState(false);

    useEffect(() => {
        let grid_search_config_url = api.gridsearch_config_file.replace("<grid_search_id>", grid_search_id);

        setError("");
        setShowHideData(false);
        setIsLoading(true);
        
        axios.get(rest_api_url+grid_search_config_url).then((response) => {
            console.log("Got response from grid_search_config_file API: ", response);
            if(response.status === 200) {
                setYamlString(response.data.trim());
                setShowHideData(true);
            }
            else {
                setError("Oops! an error occurred");
            }
            setIsLoading(false);
        })
        .catch((error) => {
            console.log("Error in grid_search_config_file: ", error);
            setIsLoading(false);
            setError("Oops! an error occurred");
        });

    },[isSocketConnected && (grid_search_id || rest_api_url || socket_connection_url)]);

    function downloadFile() {
        const blob = new Blob([yamlString], { type: 'text/yaml' });
        const url = window.URL.createObjectURL(blob!);
        const a = document.createElement('a');
        a.href = url;
        a.download = defaultGridSearchConfigFileName+".yml";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <Box className={styles.textfield_cardcontent_grid_search_config}>
                    <h2 className={styles.heading_style}>
                        Grid Search Configuration
                    </h2>
                    <div>
                    {
                        !isLoading && error.length === 0 && yamlString.length > 0 ?
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
                        !isLoading && error.length === 0 && yamlString.length > 0 ?
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
                !isLoading && error.length === 0 && Object.keys(yamlString).length > 0 && showHideData ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Card>
                        <CardContent className={styles.yaml_content_overflow}>
                            <pre>{yamlString}</pre>
                        </CardContent>
                    </Card>
                </Grid>
                :
                !isLoading && error.length !== 0 ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    <Box className={styles.error_text}>
                        Error Occured In Getting Grid Search Configuration File!
                    </Box>
                </Grid>
                :
                null
            }
        </Grid>
    );
}