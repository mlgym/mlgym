import { useCallback, useEffect, useState } from 'react';
import { settingConfigsInterface } from "../../app/App";
import { useAppSelector } from "../../app/hooks";
import { isConnected } from "../../redux/status/statusSlice";
import GridSearchConfigurations from "./GridSearchConfigurations/GridSearchConfigurations";
import SelectExperimentDropdown from "./SelectExperimentDropdown/SelectExperimentDropdown";
// mui components & styles
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
import { Box, Button, Grid, TextField } from "@mui/material";
import styles from "./Settings.module.css";

export const defaultGridSearchIdHelperText = "eg: 2022-11-06--17-59-10";
export const defaultSocketConnectionUrlHelperText = "eg: http://127.0.0.1:5002";
export const defaultRestApiUrlHelperText = "eg: http://127.0.0.1:5001";

export interface FuncProps {
    validateConfigs(value:boolean): void;
    setConfigData(configData:settingConfigsInterface): void;
}

// Settings file and Config popup file (except render part) might look exactly the same for now. But Settigns will have more functionality later. So we will add more things in Settings which will make it different from popup file.
const Settings: React.FC<FuncProps> = (props) => {

    const isSocketConnected = useAppSelector(isConnected);

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
    },[])

    function changeText(key:string, text:string) {
        setConfigTextState({ ...configTextState, [key]: text });
    }

    function clearAllText() {
        setConfigTextState({ 
            gridSearchId: "",
            socketConnectionUrl: "",
            restApiUrl: "" 
        });
        localStorage.removeItem("SettingConfigs")
    }

    function submitData() {  
        let configData = {
            gridSearchId: configTextState.gridSearchId,
            socketConnectionUrl: configTextState.socketConnectionUrl,
            restApiUrl: configTextState.restApiUrl
        }      
        props.validateConfigs(true);
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
            {
                isSocketConnected ?
                <Box className={styles.grid_search_config_contianer}>
                    <SelectExperimentDropdown />
                </Box>
                :
                null
            }
            {
                isSocketConnected ?
                <Box className={styles.grid_search_config_contianer}>
                    <GridSearchConfigurations />
                </Box>
                :
                null
            }
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
        </Box>
    )
}

export default Settings;