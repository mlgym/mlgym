import { Box, Button, TextField, Toolbar, Grid } from "@mui/material";
import { useCallback, useEffect, useState } from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
import { settingConfigsInterface } from "../../app/App";
import { getGridSearchId, getRestApiUrl, getSocketConnectionUrl, isConnected } from "../../redux/globalConfig/globalConfigSlice";
import { useAppSelector } from "../../app/hooks";
import GridSearchConfigurations from "./GridSearchConfigurations/GridSearchConfigurations";
import RunConfig from "./RunConfig/RunConfig";
// styles
import styles from "./Settings.module.css";

export const defaultGridSearchIdHelperText = "eg: 2022-11-06--17-59-10";
export const defaultSocketConnectionUrlHelperText = "eg: http://127.0.0.1:5002";
export const defaultRestApiUrlHelperText = "eg: http://127.0.0.1:5001";

export interface FuncProps {
    setSocketConnectionRequest(): void;
    setConfigData(configData:settingConfigsInterface): void;
    isConfigValidated?: boolean
}

// Settings file and Config popup file (except render part) might look exactly the same for now. But Settigns will have more functionality later. So we will add more things in Settings which will make it different from popup file.
const Settings: React.FC<FuncProps> = (props) => {

    const isSocketConnected = useAppSelector(isConnected);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);
    const socket_connection_url = useAppSelector(getSocketConnectionUrl);

    const [configTextState, setConfigTextState] = useState({
        gridSearchId: "",
        socketConnectionUrl: "",
        restApiUrl: ""
    });

    const getSettingConfigs = useCallback(async (settingConfigsInStorage:string) => {
        const data = await JSON.parse(settingConfigsInStorage);
        return data
      }, []);

    useEffect(() => {
        let settingConfigsInStorage = localStorage.getItem('SettingConfigs');
        if(settingConfigsInStorage) {
            getSettingConfigs(settingConfigsInStorage).then((settingConfigs) => {
                setConfigTextState(settingConfigs);
            });
        }
    },[isSocketConnected && (grid_search_id || rest_api_url || socket_connection_url)])

    function changeText(key:string, text:string) {
        setConfigTextState({ ...configTextState, [key]: text });
    }

    function clearAllText() {
        let reset_config_texts = { 
            gridSearchId: "",
            socketConnectionUrl: "",
            restApiUrl: "" 
        }
        setConfigTextState(reset_config_texts);
        localStorage.removeItem("SettingConfigs");
        props.setConfigData(reset_config_texts);
    }

    function submitData() {  
        let configData = {
            gridSearchId: configTextState.gridSearchId,
            socketConnectionUrl: configTextState.socketConnectionUrl,
            restApiUrl: configTextState.restApiUrl
        }      
        // props.validateConfigs(true);
        props.setSocketConnectionRequest();
        props.setConfigData(configData);
    }

    function validateData() {
        let gridSearchId = configTextState.gridSearchId;
        let socketConnectionUrl = configTextState.socketConnectionUrl;
        let restApiUrl = configTextState.restApiUrl;
        let isDataInValid = true;
        
        // basic validation check: if any values are typed by user, then enable submit button or else keep it disabled - so that empty values are not sent for socket connection request
        if(gridSearchId.trim().length > 0 && socketConnectionUrl.trim().length > 0 && restApiUrl.trim().length > 0 ) {
            isDataInValid = false;
            return isDataInValid;
        }
        return isDataInValid;
    }

    return (
        <Box>
            <Toolbar/>
            <Box className={styles.settings_main_box}>
                <Grid container rowSpacing={1} rowGap={3} spacing={{ xs: 1, md: 2, lg: 2 }} className={styles.grid_container_basic_fields}>
                    <Grid item={true} xs={12} sm={12} md={12} lg={isSocketConnected?4:12} className={styles.grid_item_basic_fields}>
                        <TextField
                            id="outlined-multiline-flexible"
                            label="Grid Search-id"
                            placeholder="Enter grid search-id here!..."
                            value={configTextState.gridSearchId}
                            onChange={(e)=>changeText("gridSearchId", e.target.value)}
                            className={isSocketConnected?styles.settings_text_box_full_width:styles.settings_text_box_less_width}
                            helperText={defaultGridSearchIdHelperText}
                            fullWidth={isSocketConnected?true:false}
                        />
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={12} lg={isSocketConnected?4:12} className={styles.grid_item_basic_fields}>
                        <TextField
                            id="outlined-multiline-flexible"
                            label="Socket Connection URL"
                            placeholder="Enter Socker Connection URL here!..."
                            value={configTextState.socketConnectionUrl}
                            onChange={(e)=>changeText("socketConnectionUrl", e.target.value)}
                            className={isSocketConnected?styles.settings_text_box_full_width:styles.settings_text_box_less_width}
                            helperText={defaultSocketConnectionUrlHelperText}
                            fullWidth={isSocketConnected?true:false}
                        />
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={12} lg={isSocketConnected?4:12} className={styles.grid_item_basic_fields}>
                        <TextField
                            id="outlined-multiline-flexible"
                            label="Rest API URL"
                            placeholder="Enter rest API URL here!..."
                            value={configTextState.restApiUrl}
                            onChange={(e)=>changeText("restApiUrl", e.target.value)}
                            className={isSocketConnected?styles.settings_text_box_full_width:styles.settings_text_box_less_width}
                            helperText={defaultRestApiUrlHelperText}
                            fullWidth={isSocketConnected?true:false}
                        />
                    </Grid>
                </Grid>
            </Box>
            <Box className={styles.setting_form_btns_box}>
                <Button 
                    variant="outlined" 
                    size="large"
                    startIcon={<DeleteIcon />}
                    onClick={()=>clearAllText()}
                >
                    Clear
                </Button>
                <Button 
                    variant="contained" 
                    size="large" 
                    endIcon={<SendIcon />}
                    onClick={()=>submitData()}
                    disabled={validateData()}
                >
                    Save
                </Button>
            </Box>
            {
                isSocketConnected ?
                <Grid container className={styles.settings_files_grid}>
                    <Grid item={true} xs={12} sm={12} md={12} lg={6}>
                        <Box className={styles.grid_search_config_contianer}>
                            <GridSearchConfigurations />
                        </Box>
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={12} lg={6}>
                        <Box className={styles.grid_search_config_contianer}>
                            <RunConfig />
                        </Box>
                    </Grid>
                </Grid>
                :
                null
            }
        </Box>
    )
}

export default Settings;