import { Card, CardContent, CardHeader, Grid, FormControl, InputLabel, MenuItem, Select } from "@mui/material";
import StorageIcon from '@mui/icons-material/Storage';
import NodesList from "./NodesList";
import GraphArea from "./GraphArea";
import { JsonViewer } from "@textea/json-viewer";
import { useState } from "react";
import PipelineDetails from "../pipelineDetails/PipelineDetails";
import GraphComponent from "../pipelineDetails/GraphComponent";
import { INode, IPipeline } from "./interface";
import usePipelineCardContext, { PipelineCardContextProvider } from "./PipelineCardContext";
import { ReactFlowProvider } from "reactflow";


export default function ({ details }: { details: IPipeline }) {
    // const [treeOrientation, setTreeOrientation] = useState("horizontal");
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
        // action={details &&
        //     <FormControl fullWidth>
        //         <InputLabel>Orientation</InputLabel>
        //         <Select
        //             value={treeOrientation}
        //             label="Orientation"
        //             onChange={(e) => setTreeOrientation(e.target.value)}
        //         >
        //             <MenuItem value={"vertical"}>vertical</MenuItem>
        //             <MenuItem value={"horizontal"}>horizontal</MenuItem>
        //         </Select>
        //     </FormControl>
        // }
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
            <Grid item>
                <ConfigViewer />
            </Grid>

            {/* {details && details[Object.keys(details)[0]]?.hasOwnProperty('nodes') ?
                        <PipelineDetails
                        pipelineDetails={details}
                        experiment_id={"ID"}
                        treeOrientationProp={treeOrientation}
                        />
                        :
                    <GraphComponent data={details} />} */}
        </Grid>
    </CardContent>
);

const ConfigViewer = () => {
    // TODO: not only the top node! when a node is click update it too!
    const { activeNodeName, pipelineDetails } = usePipelineCardContext();
    return pipelineDetails[activeNodeName].config_str ?
        <JsonViewer value={JSON.parse(pipelineDetails[activeNodeName].config_str)} rootName={activeNodeName} />
        :
        null;
};

