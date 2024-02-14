import { List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import WidgetsIcon from '@mui/icons-material/Widgets';
import usePipelineCardContext from "./PipelineCardContext";
import React from "react";


export default function () {
    const { activePipelineKey, setActivePipelineKey, availablePipelineKeys } = usePipelineCardContext();

    const listItems = availablePipelineKeys.map((pipelineKey) => (
        <Item key={pipelineKey}
            activePipelineKey={activePipelineKey}
            setActivePipelineKey={setActivePipelineKey}
            pipelineKey={pipelineKey} />
    ));

    return (
        <List>
            {listItems}
        </List>
    );
}

interface IItemProps {
    activePipelineKey: string;
    setActivePipelineKey(key: string): void;
    pipelineKey: string;
}

const Item = React.memo(({ activePipelineKey, setActivePipelineKey, pipelineKey }: IItemProps) => (
    <ListItem>
        <ListItemButton
            selected={pipelineKey === activePipelineKey}
            onClick={(event) => setActivePipelineKey(pipelineKey)}
        >
            <ListItemIcon>
                <WidgetsIcon />
            </ListItemIcon>
            <ListItemText primary={pipelineKey.replace(/_/g, " ")} />
        </ListItemButton>
    </ListItem>
));