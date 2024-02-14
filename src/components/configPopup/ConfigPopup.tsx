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

// Settings file and Config popup file (except render part) might look exactly the same for now. But Settigns will have more functionality later. So we will add more things in Settings which will make it different from popup file.
const ConfigPopup: React.FC<FuncProps> = (props) => {

    const navigate = useNavigate();

    const handleGoToSettings = () => {
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

    // regular expression in replace function replaces all the trailing backslashes and then stores the url in redux as during actual API call, we are appending the full api path with the main url

    function submitData() {
        let settingConfigs = {
            gridSearchId: configTextState.gridSearchId,
            socketConnectionUrl: configTextState.socketConnectionUrl.replace(/\/+$/, ''),
            restApiUrl: configTextState.restApiUrl.replace(/\/+$/, '')
        }
        props.setSocketConnectionRequest();
        props.setConfigData(settingConfigs);
    }

    function validateData() {
        let gridSearchId = configTextState.gridSearchId;
        let socketConnectionUrl = configTextState.socketConnectionUrl.replace(/\/+$/, '');
        let restApiUrl = configTextState.restApiUrl.replace(/\/+$/, '');
        let isDataInValid = true;

        // basic validation check: if any values are typed by user, then enable submit button or else keep it disabled - so that empty values are not sent for socket connection request
        if(gridSearchId.trim().length > 0 && socketConnectionUrl.trim().length > 0 && restApiUrl.trim().length > 0 ) {
            isDataInValid = false;
            return isDataInValid;
        }
        return isDataInValid;
    }

    return(
        <Dialog open={!props.isConfigValidated}>
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