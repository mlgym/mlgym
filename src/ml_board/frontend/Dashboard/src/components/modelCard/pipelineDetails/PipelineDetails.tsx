import { useEffect, useState } from 'react';
import { JsonViewer } from "@textea/json-viewer";
import StorageIcon from '@mui/icons-material/Storage';
import WidgetsIcon from '@mui/icons-material/Widgets';
import { AnyKeyValuePairs } from '../../../app/interfaces';
import { Chip, Container, Typography } from "@mui/material";
import ReactFlow, { Background, ReactFlowProvider } from "reactflow";
import { add_nodes_and_edges, getObjectByKey, getParentObjects } from "./PipelineDetailsHelpers";
import { Card, CardHeader, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import styles from "./pipelineDetails.module.css";

export default function PipelineDetails({pipelineDetails} : {pipelineDetails: AnyKeyValuePairs}) {

    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [selectedNode, setSelectedNode] = useState(undefined);
    const [selectedNodeConfig, setSelectedNodeConfig] = useState(undefined);
    const [selectedNodeRequirements, setSelectedNodeRequirements] = useState([]);
    const [selectedPipelineKey, setSelectedPipelineKey] = useState("");
    const [listVisibility, setListVisibility] = useState(true)
    
    useEffect(()=>{
        let selectedKey = ""
        if(selectedPipelineKey !== ""){
            selectedKey = selectedPipelineKey
        }else{
            selectedKey = Object.keys(pipelineDetails)[0]
        }
        setSelectedPipelineKey(selectedKey)

        let selectedModule = pipelineDetails[selectedKey]

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

        setNodes(selectedModuleNodes)

        setEdges(selectedModuleEdges)

    },[pipelineDetails, selectedPipelineKey])

    const handlePipelineKeyChange = (pipelineKey: string) => {
        setSelectedPipelineKey(pipelineKey)
        setSelectedNode(undefined)
        setSelectedNodeConfig(undefined)
        setSelectedNodeRequirements([])
    };

    const toggleList = () => {
        setListVisibility(!listVisibility)
    }

    const setSelectedNodeData = (node: AnyKeyValuePairs) => {

        setSelectedNode(node.id)

        let selectedNodeData = getObjectByKey(pipelineDetails, node.id)

        if(selectedNodeData.hasOwnProperty('config_str')) {
            setSelectedNodeConfig(JSON.parse(selectedNodeData.config_str))
        }
        else {
            setSelectedNodeConfig(undefined)
        }

        let selectedNodeRequiredData: string[] = getParentObjects(pipelineDetails, node.id)
        selectedNodeRequiredData = selectedNodeRequiredData.filter((name: string) => name !== node.id)
        let a:any = [...new Set(selectedNodeRequiredData)]
        setSelectedNodeRequirements(a)
    }

    return(
        <Card raised sx={{ mb: 2, borderRadius: 2 }}>
            <CardHeader
                avatar={<StorageIcon onClick={()=>toggleList()} style={styles.storage_icon_hover}/>}
                title={<strong>Pipeline Graph</strong>}
                sx={{
                    px: 3, py: 2,
                    borderBottom: "1px solid black",
                }}
            />
            <div style={styles.main_container}>
                {
                    listVisibility ?
                    <List style={styles.list}>
                        {
                            Object.keys(pipelineDetails).map((pipelineKey: string) => (
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
                    :
                    null
                }
                <div style={styles.pipeline_graph_area}>
                    <ReactFlowProvider>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            deleteKeyCode={null}
                            snapToGrid={true}
                            onNodeClick={(event:React.MouseEvent, node:AnyKeyValuePairs)=>setSelectedNodeData(node)}
                        >
                            <Background />
                        </ReactFlow>
                    </ReactFlowProvider>
                </div>
                {
                    selectedNode ?
                    <div style={styles.node_data_configs}
                    >
                        <div>
                            <Container fixed sx={{ marginTop: 1 }}>
                                <Typography variant="subtitle2" display="inline">
                                    <strong>{selectedNode}</strong> <i>requires : </i>
                                </Typography>
                                {
                                    selectedNodeRequirements.length > 0 ?    
                                    <div>
                                        {
                                            selectedNodeRequirements.map((item:string) => {
                                                return(
                                                    <Chip 
                                                        key={item} 
                                                        label={item} 
                                                        variant="outlined" 
                                                        sx={{ marginX: 0.2, marginY: 0.5 }} 
                                                    />
                                                )
                                            })}
                                    </div>
                                    :
                                    <Typography variant="subtitle2" display="inline">
                                        None
                                    </Typography>
                                }
                            </Container>
                        </div>
                        <div>
                            <Container fixed sx={{ marginTop: 0.5 }}>
                                <Typography variant="subtitle2" display="inline">
                                    <strong>{selectedNode}</strong> <i>config : </i>
                                </Typography>
                                <JsonViewer value={selectedNodeConfig} rootName={selectedNode} />
                            </Container>
                        </div>
                    </div>
                    :
                    null
                }
            </div>
        </Card>
    )
}