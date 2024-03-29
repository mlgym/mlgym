import { Grid, Card, CardContent, IconButton, Box, LinearProgress, FormControl, FormHelperText, InputLabel, MenuItem, Select } from '@mui/material';
import { Download } from '@mui/icons-material';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api from '../../../app/ApiMaster';
import { useAppSelector } from "../../../app/hooks";
import { getGridSearchId, getRestApiUrl } from '../../../redux/globalConfig/globalConfigSlice';
import styles from './CheckpointConfigurations.module.css';

interface CheckpointDataInterface {
    "experiment_id": string,
    "epoch": string,
    "checkpoints": Array<string>
}

export default function CheckpointConfigurations({experimentIdProp} : {experimentIdProp: string}) {

    const [selectedCheckpointIndex, setSelectedCheckpointIndex] = useState(0);
    const [checkpointResourceNames, setCheckpointResourceNames] = useState(Array<string>);
    const [checkpointData, setCheckpointData] = useState(Array<CheckpointDataInterface>);
    const [error, setError] = useState("");
    const [errorInGettingResource, setErrorInGettingResource] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingResource, setIsLoadingResource] = useState(false);

    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);

    useEffect(() => {
        if(experimentIdProp) {
            getAllCheckpoints();
        }
    },[experimentIdProp]);

    function getAllCheckpoints() {
        let all_checkpoints = api.checkpoint_list.replace("<grid_search_id>", grid_search_id);
        all_checkpoints = all_checkpoints.replace("<experiment_id>", experimentIdProp);

        axios.get(rest_api_url + all_checkpoints).then((response) => {
            console.log("Got response from checkpoint_list API: ", response);
            if (response.status === 200) {
                let resp_data = response.data;
                setCheckpointData(resp_data);
                // selecting all the resource names to display for the first default index 
                setCheckpointResourceNames(resp_data[0].checkpoints);
            }
            else {
                setError("Error occured / No checkpoints available");
            }
            setIsLoading(false);
        })
        .catch((error) => {
            console.log("Error in checkpoint_list: ", error);
            setIsLoading(false);
            setError("Error occured / No checkpoints available");
        });
    }

    function getCheckpointResource(resourceName: string) {
        let checkpoint_resource = api.checkpoint_resource.replace("<grid_search_id>", grid_search_id);
        checkpoint_resource = checkpoint_resource.replace("<experiment_id>", experimentIdProp);
        checkpoint_resource = checkpoint_resource.replace("<checkpoint_id>", checkpointData[selectedCheckpointIndex].epoch.toString());
        checkpoint_resource = checkpoint_resource.replace("<checkpoint_resource>", resourceName);

        setErrorInGettingResource("");
        setIsLoadingResource(true);

        axios.get(rest_api_url + checkpoint_resource).then((response) => {
            console.log("Got response from checkpoint_resource API: ", response);
            if (response.status === 200) {
                downloadFile(resourceName, new Blob([response.data]));
            }
            else {
                setErrorInGettingResource("Oops! an error occurred in getting & downloading checkpoint resource data")
            }
            setIsLoadingResource(false);
        })
        .catch((error) => {
            console.log("Error in checkpoint_resource API: ", error);
            setIsLoadingResource(false);
            setErrorInGettingResource("Oops! an error occurred in getting & downloading checkpoint resource data")
        });
    }

    function downloadFile(resourceName: string, fileData: Blob) {
        const url = window.URL.createObjectURL(fileData!);
        const a = document.createElement('a');
        a.href = url;
        a.download = resourceName+"_checkpoint_"+checkpointData[selectedCheckpointIndex].epoch.trim().toString()+"_experiemnt_"+experimentIdProp+".pickle";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <Box className={styles.textfield_cardcontent_checkpoint_config}>
                    <FormControl fullWidth={true} error={error.length > 0}>
                        <InputLabel id="demo-simple-select-helper-label">Select Checkpoint Id</InputLabel>
                        <Select
                            labelId="demo-simple-select-helper-label"
                            id="demo-simple-select-helper"
                            value={selectedCheckpointIndex}
                            label="Select Checkpoint Id"
                            onChange={(e)=>{
                                let index = Number(e.target.value);
                                setSelectedCheckpointIndex(index);
                                setCheckpointResourceNames(checkpointData[index].checkpoints);
                            }}
                            MenuProps={{ style: { maxHeight: "250px" } }} // have to keep style here. keeping it in css file is not working for this
                        >
                            {
                                checkpointData.length > 0 ?
                                checkpointData.map((chkpt_obj, index) => 
                                    <MenuItem key={index} value={index.toString()}>
                                        {chkpt_obj.epoch}
                                    </MenuItem>
                                )
                                :
                                null
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
                !isLoading && error.length === 0 && checkpointResourceNames.length > 0 ?
                <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                    {
                        checkpointResourceNames.map((resourceName, index) => {
                            return(
                                <Card className={styles.checkpoint_data_resources_main_card} key={index}>
                                    <CardContent className={styles.checkpoint_data_resources}>
                                        <div>
                                            {resourceName}
                                        </div>
                                        <IconButton 
                                            size="small"
                                            onClick={()=>getCheckpointResource(resourceName)}
                                            disabled={isLoadingResource}
                                        >
                                            <Download /> 
                                        </IconButton>
                                    </CardContent>
                                </Card>
                            );
                        })
                    }
                    {
                        isLoadingResource ?
                        <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                            <Box>
                                <LinearProgress />
                            </Box>
                        </Grid>
                        :
                        null
                    }
                    {
                        errorInGettingResource.length > 0 ?
                        <div className={styles.error_text}>
                            {errorInGettingResource}
                        </div>
                        :
                        null
                    }
                </Grid>
                :
                null
            }
        </Grid>
    );
}