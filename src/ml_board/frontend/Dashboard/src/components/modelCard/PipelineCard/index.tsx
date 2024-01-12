import { Card, CardContent, CardHeader, Grid } from "@mui/material";
import StorageIcon from '@mui/icons-material/Storage';
import NodesList from "./NodesList";
import GraphArea from "./GraphArea";
import { IPipeline } from "./interface";
import { PipelineCardContextProvider } from "./PipelineCardContext";
import { ReactFlowProvider } from "reactflow";
import ConfigViewer from "./ConfigViewer";
import RequirementsViewer from "./RequirementsViewer";


export default function ({ details }: { details: IPipeline }) {
    return (
        <Card raised sx={{ mb: 2, borderRadius: 2 }}>
            <Header />
            <PipelineCardContextProvider pipelineDetails={details}>
                <Content />
            </PipelineCardContextProvider>
        </Card>
    );
}

const Header = () => (
    <CardHeader
        avatar={<StorageIcon />}
        title={<strong>Pipeline Graph</strong>}
        sx={{
            px: 3, py: 2,
            borderBottom: "1px solid black",
        }}
    />
);

const Content = () => (
    <CardContent>
        <Grid container>
            <Grid item>
                <NodesList />
            </Grid>
            <Grid item flexGrow={1}>
                <ReactFlowProvider>
                    <GraphArea />
                </ReactFlowProvider>
            </Grid>
            <Grid item container xs="auto" direction="column">
                <Grid item>
                    <ConfigViewer />
                </Grid>
                <Grid item>
                    <RequirementsViewer />
                </Grid>
            </Grid>
        </Grid>
    </CardContent>
);

