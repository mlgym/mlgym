import { Box, Button, TextField, Toolbar } from "@mui/material";
import { useState } from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
// styles
import styles from "./Settings.module.css";

export interface dataValidationResult {
    isDataValid: boolean;
    gridSearchIdErrorText: string;
    socketConnectionUrlErrorText: string;
    restApiUrlErrorText: string;
}
export const defaultGridSearchIdHelperText = "eg: 2022-11-06--17-59-10";
export const defaultSocketConnectionUrlHelperText = "eg: http://127.0.0.1:5002";
export const defaultRestApiUrlHelperText = "eg: http://127.0.0.1:5001";

function Settings() {

    const [configTextState, setConfigTextState] = useState({
        gridSearchId: "",
        socketConnectionUrl: "",
        restApiUrl: ""
    })

    const [errorTextState, setErrorText] = useState({
        gridSearchIdErrorText: "",
        socketConnectionUrlErrorText: "",
        restApiUrlErrorText: ""
    })

    function changeText(key:string, text:string) {
        setConfigTextState({ ...configTextState, [key]: text });
        setErrorText({...errorTextState, [key+"ErrorText"]: ""});
    }

    function clearAllText() {
        setConfigTextState({ 
            gridSearchId: "",
            socketConnectionUrl: "",
            restApiUrl: "" 
        });
        setErrorText({
            gridSearchIdErrorText: "",
            socketConnectionUrlErrorText: "",
            restApiUrlErrorText: ""
        });
    }

    function submitData() {        
        let dataValidationResult = validateData();
        if (dataValidationResult.isDataValid) {
            localStorage.setItem('SettingConfigs', JSON.stringify({
                gridSearchId: configTextState.gridSearchId,
                socketConnectionUrl: configTextState.socketConnectionUrl,
                restApiUrl: configTextState.restApiUrl
            }));
            sendDataToAPi()
        }
        else {
            if (dataValidationResult.restApiUrlErrorText !== "") {
                setErrorText({ ...errorTextState, gridSearchIdErrorText: dataValidationResult.gridSearchIdErrorText });
            }
            if (dataValidationResult.restApiUrlErrorText !== "") {
                setErrorText({ ...errorTextState, socketConnectionUrlErrorText: dataValidationResult.socketConnectionUrlErrorText });
            }
            if (dataValidationResult.restApiUrlErrorText !== "") {
                setErrorText({ ...errorTextState, restApiUrlErrorText: dataValidationResult.restApiUrlErrorText });
            }
        }
    }

    function checkToKeepDisableBtn() {
       if (errorTextState.gridSearchIdErrorText !== "" || errorTextState.socketConnectionUrlErrorText !== "" || errorTextState.restApiUrlErrorText !== "") {
            return true;
        }
        else {
            let dataValidationResult = validateData();
            if (dataValidationResult.isDataValid) {
                return false;
            }
            else {
                return true;
            }
        }
    }

    function validateData() {
        let gridSearchId = configTextState.gridSearchId
        let socketConnectionUrl = configTextState.socketConnectionUrl
        let restApiUrl = configTextState.restApiUrl
        let dataValidationResult:dataValidationResult = {
            isDataValid: false,
            gridSearchIdErrorText: "",
            socketConnectionUrlErrorText: "",
            restApiUrlErrorText: ""
        }

        if(gridSearchId.trim().length > 0) {
            if(socketConnectionUrl.trim().length > 0)
            {
                if(restApiUrl.trim().length > 0)
                {
                    dataValidationResult.isDataValid = true
                    return dataValidationResult
                }
                else
                {
                    dataValidationResult.restApiUrlErrorText = "Please enter valid Rest Api Url"
                }
            }
            else
            {
                dataValidationResult.socketConnectionUrlErrorText = "Please enter valid Socket Connection Url"
            }
        }
        else
        {
            dataValidationResult.gridSearchIdErrorText = "Please enter valid Grid Search Id";
        }
        return dataValidationResult
    }

    function sendDataToAPi() {
        
    }

    return (
        <Box>
            <Toolbar/>
            <Box className={styles.settings_main_box}>
                <TextField
                    id="outlined-multiline-flexible"
                    label="Grid Search-id"
                    placeholder="Enter grid search-id here!..."
                    value={configTextState.gridSearchId}
                    onChange={(e)=>changeText("gridSearchId", e.target.value)}
                    className={styles.settings_text_box}
                    error={
                        errorTextState.gridSearchIdErrorText !== "" ?
                        true
                        :
                        false
                    }
                    helperText={
                        errorTextState.gridSearchIdErrorText !== "" ?
                        errorTextState.gridSearchIdErrorText
                        :
                        defaultGridSearchIdHelperText
                    }
                />
                <br/>
                <TextField
                    id="outlined-multiline-flexible"
                    label="Socket Connection URL"
                    placeholder="Enter Socker Connection URL here!..."
                    value={configTextState.socketConnectionUrl}
                    onChange={(e)=>changeText("socketConnectionUrl", e.target.value)}
                    className={styles.settings_text_box}
                    error={
                        errorTextState.socketConnectionUrlErrorText !== "" ?
                        true
                        :
                        false
                    }
                    helperText={
                        errorTextState.socketConnectionUrlErrorText !== "" ?
                        errorTextState.socketConnectionUrlErrorText
                        :
                        defaultSocketConnectionUrlHelperText
                    }
                />
                <br/>
                <TextField
                    id="outlined-multiline-flexible"
                    label="Rest API URL"
                    placeholder="Enter rest API URL here!..."
                    value={configTextState.restApiUrl}
                    onChange={(e)=>changeText("restApiUrl", e.target.value)}
                    className={styles.settings_text_box}
                    error={
                        errorTextState.restApiUrlErrorText !== "" ?
                        true
                        :
                        false
                    }
                    helperText={
                        errorTextState.restApiUrlErrorText !== "" ?
                        errorTextState.restApiUrlErrorText
                        :
                        defaultRestApiUrlHelperText
                    }
                />
                <br/>
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
                        disabled={checkToKeepDisableBtn()}
                    >
                        Save
                    </Button>
                </Box>
            </Box>
        </Box>
    )
}

export default Settings;