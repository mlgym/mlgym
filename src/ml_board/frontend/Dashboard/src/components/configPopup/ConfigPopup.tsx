import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { RoutesMapping } from '../../app/RoutesMapping';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { dataValidationResult, defaultGridSearchIdHelperText, defaultSocketConnectionUrlHelperText, defaultRestApiUrlHelperText } from '../settings/Settings';

interface FuncProps {
    validateConfigs(value:boolean): void;
}

const ConfigPopup: React.FC<FuncProps> = (props) => {

    const navigate = useNavigate();

    const [open, setOpen] = useState(true);

    const handleGoToSettings = () => {
        setOpen(false);
        navigate(RoutesMapping.Settings.url)
    };

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
        setErrorText({...errorTextState, [key+"ErrorText"]: ""});
    }

    function submitData() {
        let dataValidationResult = validateData();
        if (dataValidationResult.isDataValid) {
            localStorage.setItem('SettingConfigs', JSON.stringify({
                gridSearchId: configTextState.gridSearchId,
                socketConnectionUrl: configTextState.socketConnectionUrl,
                restApiUrl: configTextState.restApiUrl
            }));
            sendDataToAPi();
        }
        else {
            if (dataValidationResult.gridSearchIdErrorText !== "") {
                setErrorText({ ...errorTextState, gridSearchIdErrorText: dataValidationResult.gridSearchIdErrorText });
            }
            if (dataValidationResult.socketConnectionUrlErrorText !== "") {
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
        setOpen(false);
        props.validateConfigs(true);
    }

    return(
        <Dialog open={open}>
            <DialogTitle>Enter Configurations</DialogTitle>
            <DialogContent>
            <DialogContentText>
                To subscribe to your experiment results, please enter grid search id, socket connection url and rest api url here. OR, you can go to settings page to add more configurations.
            </DialogContentText>
            <TextField
                autoFocus
                margin="dense"
                label="Grid Search-id"
                fullWidth
                variant="standard"
                value={configTextState.gridSearchId}
                onChange={(e)=>changeText("gridSearchId", e.target.value)}
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
            <TextField
                margin="dense"
                label="Socket Connection Url"
                fullWidth
                variant="standard"
                value={configTextState.socketConnectionUrl}
                onChange={(e)=>changeText("socketConnectionUrl", e.target.value)}
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
            <TextField
                margin="dense"
                label="Rest API Url"
                fullWidth
                variant="standard"
                value={configTextState.restApiUrl}
                onChange={(e)=>changeText("restApiUrl", e.target.value)}
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
            </DialogContent>
            <DialogActions>
                <Button 
                    disabled={checkToKeepDisableBtn()}
                    onClick={()=>submitData()}
                >
                    Save
                </Button>
                <Button onClick={()=>handleGoToSettings()}>Go to Settings</Button>
            </DialogActions>
        </Dialog>
    );
}

export default ConfigPopup;