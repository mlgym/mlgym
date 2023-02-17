import { Box, Button, TextField, Toolbar } from "@mui/material";
import { useState } from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';

function Settings() {

    const [state, setState] = useState({
        gridSearchId: "",
        socketConnectionUrl: "",
        restApiUrl: ""
    })

    function changeText(key:string, text:string) {
        setState({ ...state, [key]: text });
    }

    function clearAllText() {
        setState({ 
            gridSearchId: "",
            socketConnectionUrl: "",
            restApiUrl: "" 
        });
    }

    function submitData() {
        
    }

    return (
        <div>
            <Toolbar/>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    paddingLeft: 20,
                    paddingRight: 20,
                    paddingTop: 10,
                    paddingBottom: 10
                }}
            >
                <TextField
                    id="outlined-multiline-flexible"
                    label="Grid Search-id"
                    placeholder="Enter grid search-id here!..."
                    value={state["gridSearchId"]}
                    onChange={(e)=>changeText("gridSearchId", e.target.value)}
                    sx={{
                        marginBottom: 5
                    }}
                />
                <TextField
                    id="outlined-multiline-flexible"
                    label="Socket Connection URL"
                    placeholder="Enter Socker Connection URL here!..."
                    value={state["socketConnectionUrl"]}
                    onChange={(e)=>changeText("socketConnectionUrl", e.target.value)}
                    sx={{
                        marginBottom: 5
                    }}
                />
                <TextField
                    id="outlined-multiline-flexible"
                    label="Rest API URL"
                    placeholder="Enter rest API URL here!..."
                    value={state["restApiUrl"]}
                    onChange={(e)=>changeText("restApiUrl", e.target.value)}
                    sx={{
                        marginBottom: 5
                    }}
                />
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "row",
                        alignItems: "center",
                        justifyContent: "center"
                    }}
                >
                    <Button 
                        variant="outlined" 
                        size="large"
                        startIcon={<DeleteIcon />}
                        sx={{
                            width: "20%",
                            marginRight: 2
                        }}
                        onClick={()=>clearAllText()}
                    >
                        Clear
                    </Button>
                    <Button 
                        variant="contained" 
                        size="large" 
                        endIcon={<SendIcon />}
                        sx={{
                            width: "20%",
                            marginLeft: 2
                        }}
                        onClick={()=>submitData()}
                    >
                        Submit
                    </Button>
                </Box>
            </Box>
        </div>
    )
}

export default Settings;