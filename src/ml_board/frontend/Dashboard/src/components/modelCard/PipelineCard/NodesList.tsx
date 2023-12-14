import { List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import WidgetsIcon from '@mui/icons-material/Widgets';
import usePipelineCardContext from "./PipelineCardContext";


export default function () {
    const { activeNode, setActivePipelineKey, availablePipelineKeys } = usePipelineCardContext();

    const listItems = availablePipelineKeys.map((pipelineKey) => (
        <ListItem key={pipelineKey}>
            <ListItemButton
                selected={pipelineKey === activeNode}
                onClick={(event) => setActivePipelineKey(pipelineKey)}
            >
                <ListItemIcon>
                    <WidgetsIcon />
                </ListItemIcon>
                <ListItemText primary={pipelineKey} />
            </ListItemButton>
        </ListItem>
    ));

    return (
        <List>
            {listItems}
        </List>
    );
}