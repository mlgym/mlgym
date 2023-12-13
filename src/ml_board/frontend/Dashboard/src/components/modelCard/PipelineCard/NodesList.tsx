import { List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import WidgetsIcon from '@mui/icons-material/Widgets';
import usePipelineCardContext from "./PipelineCardContext";


export default function () {
    const { activeNodeName, pipelineDetails, setActiveNodeName } = usePipelineCardContext();

    const listItems = Object.keys(pipelineDetails).map((thisNodesName) => (
        <ListItem key={thisNodesName}>
            <ListItemButton
                selected={thisNodesName === activeNodeName}
                onClick={(event) => setActiveNodeName(thisNodesName)}
            >
                <ListItemIcon>
                    <WidgetsIcon />
                </ListItemIcon>
                <ListItemText primary={thisNodesName} />
            </ListItemButton>
        </ListItem>
    ));

    return (
        <List>
            {listItems}
        </List>
    );
}