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
import { FuncProps } from "../settings/Settings";
import { defaultGridSearchIdHelperText, defaultSocketConnectionUrlHelperText, defaultRestApiUrlHelperText } from '../settings/Settings';

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

    function submitData() {
        let settingConfigs = {
            gridSearchId: configTextState.gridSearchId,
            socketConnectionUrl: configTextState.socketConnectionUrl,
            restApiUrl: configTextState.restApiUrl
        }      
        setOpen(false);
        props.validateConfigs(true);
        props.setConfigData(settingConfigs);
    }

    function validateData() {
        let gridSearchId = configTextState.gridSearchId;
        let socketConnectionUrl = configTextState.socketConnectionUrl;
        let restApiUrl = configTextState.restApiUrl;
        let isDataInValid = true;

        if(gridSearchId.trim().length > 0 && socketConnectionUrl.trim().length > 0 && restApiUrl.trim().length > 0 ) {
            isDataInValid = false;
            return isDataInValid;
        }
        return isDataInValid;
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
                helperText={defaultGridSearchIdHelperText}
            />
            <TextField
                margin="dense"
                label="Socket Connection Url"
                fullWidth
                variant="standard"
                value={configTextState.socketConnectionUrl}
                onChange={(e)=>changeText("socketConnectionUrl", e.target.value)}
                helperText={defaultSocketConnectionUrlHelperText}
            />
            <TextField
                margin="dense"
                label="Rest API Url"
                fullWidth
                variant="standard"
                value={configTextState.restApiUrl}
                onChange={(e)=>changeText("restApiUrl", e.target.value)}
                helperText={defaultRestApiUrlHelperText}
            />
            </DialogContent>
            <DialogActions>
                <Button 
                    disabled={validateData()}
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