import { Chip, Container, Typography } from "@mui/material";
import usePipelineCardContext from "./PipelineCardContext";

export default function RequirementsViewer() {
    const { activeNode, activePipeline } = usePipelineCardContext();

    const nodeData = activePipeline?.nodes.find(node => node.id === activeNode)!.data;
    const requirements = nodeData.requirements ?? [];

    return requirements.length == 0 ? null : (<>
        <Container fixed>
            <Typography variant="subtitle2" display="inline">
                <strong>{activeNode}</strong> <i>requires : </i>
            </Typography>
            {requirements.map(item => <Chip key={item} label={item} variant="outlined" sx={{ marginX: 0.2 }} />)}
        </Container>
    </>);
};

