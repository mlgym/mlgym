import { useEffect, useState } from 'react';
import StorageIcon from '@mui/icons-material/Storage';
import WidgetsIcon from '@mui/icons-material/Widgets';
import { AnyKeyValuePairs } from '../../../app/interfaces';
import ReactFlow, { Background, ReactFlowProvider, MarkerType } from "reactflow";
import { Card, CardHeader, Grid, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
// import 'reactflow/dist/style.css'; // original css from react flow => found in node_modules
import "./pipelineDetails.css" // copied the original css and made changes in it. See line 233, 234 & 242

function add_nodes_and_edges(parentKey: string, selectedModule: any, selectedModuleNodes: any, selectedModuleEdges: any, x:number, y:number) {

    y = y+100

    Object.keys(selectedModule.nodes).map((new_node: any, indx: any) => {
        if (indx !== 0) {
            x = x + 150*(indx+1) // Note: if you change width in css at line 234, then change `150` to desired number to shift the nodes at same level
        }
        selectedModuleNodes.push({
            id: new_node,
            position: { x: x, y: y }, 
            data: { 
                label: new_node
            }
        })
        selectedModuleEdges.push({
            id: `edge-${parentKey}-${new_node}`, 
            source: parentKey, 
            target: new_node,
            markerEnd: { type: MarkerType.Arrow }
        })
        if(selectedModule.nodes[new_node].nodes){
            let arr = add_nodes_and_edges(new_node, selectedModule.nodes[new_node], selectedModuleNodes, selectedModuleEdges, x, y)
            selectedModuleNodes = arr[0]
            selectedModuleEdges = arr[1]
        }
    })

    return [selectedModuleNodes, selectedModuleEdges]
}
export default function PipelineDetails({pipelineDetails} : {pipelineDetails: AnyKeyValuePairs}) {

    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [selectedPipelineKey, setSelectedPipelineKey] = useState("");
    
    useEffect(()=>{
        console.log("pipelineDetails = ",pipelineDetails)
        let selectedKey = ""
        if(selectedPipelineKey !== ""){
            selectedKey = selectedPipelineKey
        }else{
            selectedKey = Object.keys(pipelineDetails)[0]
        }
        console.log("selectedKey = ",selectedKey)
        setSelectedPipelineKey(selectedKey)

        let selectedModule = pipelineDetails[selectedKey]
        console.log("selectedModule = ",selectedModule)

        let x = 100 // can start with any position. sub-nodes will adapt accordingly
        let y = 20 // can start with any position. sub-nodes will adapt accordingly
        let selectedModuleNodes: any = []
        let selectedModuleEdges: any = []

        selectedModuleNodes.push({
            id: selectedKey,
            position: { x: x, y: y }, 
            data: { 
                label: selectedKey
            }
        });

        let arr = add_nodes_and_edges(selectedKey, selectedModule, selectedModuleNodes, selectedModuleEdges, x, y)
        selectedModuleNodes = arr[0]
        selectedModuleEdges = arr[1]

        console.log("selectedModuleNodes = ",selectedModuleNodes)
        setNodes(selectedModuleNodes)

        console.log("selectedModuleEdges = ",selectedModuleEdges)
        setEdges(selectedModuleEdges)

    },[pipelineDetails, selectedPipelineKey])

    const handlePipelineKeyChange = (pipelineKey: any) => {
        setSelectedPipelineKey(pipelineKey)
    };

    return(
        <Card raised sx={{ mb: 2, borderRadius: 2 }}>
            <CardHeader
                avatar={<StorageIcon style={{ cursor: "pointer" }}/>}
                title={<strong>Pipeline Graph</strong>}
                sx={{
                    px: 3, py: 2,
                    borderBottom: "1px solid black",
                }}
            />
            <Grid container>
                <Grid item>
                    <List>
                        {
                            Object.keys(pipelineDetails).map((pipelineKey: any) => (
                                <ListItem key={pipelineKey}>
                                    <ListItemButton
                                        selected={pipelineKey === selectedPipelineKey}
                                        onClick={()=>handlePipelineKeyChange(pipelineKey)}
                                    >
                                        <ListItemIcon>
                                            <WidgetsIcon />
                                        </ListItemIcon>
                                        <ListItemText primary={pipelineKey} />
                                    </ListItemButton>
                                </ListItem>
                            ))
                        }
                    </List>
                </Grid>
                <Grid item flexGrow={1}>
                    <ReactFlowProvider>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            deleteKeyCode={null}
                            snapToGrid={true}
                        >
                            <Background />
                        </ReactFlow>
                    </ReactFlowProvider>
                </Grid>
                <Grid item container xs="auto" direction="column">
                    <Grid item>
                        {/* TODO: add requirements chips */}
                    </Grid>
                    <Grid item>
                        {/* TODO: add json config viewer */}
                    </Grid>
                </Grid>
            </Grid>
        </Card>
    )
}