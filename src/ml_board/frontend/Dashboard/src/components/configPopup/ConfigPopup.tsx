import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { RoutesMapping } from '../../app/RoutesMapping';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

function ConfigPopup() {

    const navigate = useNavigate();

    const [open, setOpen] = useState(true);

    const handleGoToSettings = () => {
        setOpen(false);
        navigate(RoutesMapping.Settings.url)
    };

    const handleClose = () => {
        setOpen(false);
    };

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
            />
            <TextField
                margin="dense"
                label="Socket Connection Url"
                fullWidth
                variant="standard"
            />
            <TextField
                margin="dense"
                label="Rest API Url"
                fullWidth
                variant="standard"
            />
            </DialogContent>
            <DialogActions>
            <Button onClick={handleGoToSettings}>Go to Settings</Button>
            <Button onClick={handleClose}>Save</Button>
            </DialogActions>
        </Dialog>
    );
}

export default ConfigPopup;