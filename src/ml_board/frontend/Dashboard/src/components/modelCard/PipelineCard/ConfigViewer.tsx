import { JsonViewer } from "@textea/json-viewer";
import usePipelineCardContext from "./PipelineCardContext";
import { Container, Typography } from "@mui/material";

export default function ConfigViewer() {
    const { activeNode, activePipeline } = usePipelineCardContext();

    const config = activePipeline?.nodes.find(node => node.id === activeNode)!.data.config;

    return config ? <Container fixed>
        <Typography variant="subtitle2" display="inline">
            <strong>{activeNode}</strong> <i>config : </i>
        </Typography>
        <JsonViewer value={config} rootName={activeNode} />
    </Container>
        : null;
};

