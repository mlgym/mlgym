import { useEffect, useState } from 'react';
import { JsonViewer } from "@textea/json-viewer";
import StorageIcon from '@mui/icons-material/Storage';
import WidgetsIcon from '@mui/icons-material/Widgets';
import { AnyKeyValuePairs } from '../../../app/interfaces';
import { Chip, Container, Typography } from "@mui/material";
import ReactFlow, { Background, ReactFlowProvider, MarkerType } from "reactflow";
import { Card, CardHeader, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import "./pipelineDetails.css"

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

function getObjectByKey(obj:any, key:any) {
    let result:any = [];
  
    function search(obj:any) {
      for (let prop in obj) {
        if (obj.hasOwnProperty(prop)) {
          if (prop === key) {
            result.push(obj[prop]);
          } else if (typeof obj[prop] === 'object') {
            search(obj[prop]);
          }
        }
      }
    }
  
    search(obj);
    return result[0];
}

function getParentObjects(jsonObj: any, targetKeyName: string, parentObjects: string[] = [], currentPath: string = ''): string[] {
    for (const key in jsonObj) {
        if (jsonObj.hasOwnProperty(key)) {
            let newPath = currentPath ? `${currentPath}.${key}` : key;
            if (key === targetKeyName) {
                let names = newPath.split(".").filter(name => name !== "nodes")
                parentObjects.push(...names);
            } else if (typeof jsonObj[key] === 'object') {
                getParentObjects(jsonObj[key], targetKeyName, parentObjects, newPath);
            }
        }
    }
    return parentObjects;
}

export default function PipelineDetails({pipelineDetails} : {pipelineDetails: AnyKeyValuePairs}) {

    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [selectedNode, setSelectedNode] = useState(undefined);
    const [selectedNodeConfig, setSelectedNodeConfig] = useState(undefined);
    const [selectedNodeRequirements, setSelectedNodeRequirements] = useState([]);
    const [selectedPipelineKey, setSelectedPipelineKey] = useState("");
    const [listVisibility, setListVisibility] = useState(true)
    
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
        setSelectedNode(undefined)
        setSelectedNodeConfig(undefined)
        setSelectedNodeRequirements([])
    };

    const toggleList = () => {
        setListVisibility(!listVisibility)
    }

    const setSelectedNodeData = (node: any) => {

        console.log("node = ",node.id)
        setSelectedNode(node.id)

        let selectedNodeData = getObjectByKey(pipelineDetails, node.id)
        console.log("selectedNodeData = ",selectedNodeData)

        if(selectedNodeData.hasOwnProperty('config_str')) {
            setSelectedNodeConfig(JSON.parse(selectedNodeData.config_str))
        }
        else {
            setSelectedNodeConfig(undefined)
        }

        let selectedNodeRequiredData:any = getParentObjects(pipelineDetails, node.id)
        selectedNodeRequiredData = selectedNodeRequiredData.filter((name:any) => name !== node.id)
        let a: any = [... new Set(selectedNodeRequiredData)]
        console.log("a = ",a)
        setSelectedNodeRequirements(a)
    }

    return(
        <Card raised sx={{ mb: 2, borderRadius: 2 }}>
            <CardHeader
                avatar={<StorageIcon onClick={()=>toggleList()} style={{ cursor: "pointer" }}/>}
                title={<strong>Pipeline Graph</strong>}
                sx={{
                    px: 3, py: 2,
                    borderBottom: "1px solid black",
                }}
            />
            <div style={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "space-between",
                gap: "2px"
            }}>
                {
                    listVisibility ?
                    <List style={{
                        width: "400px"
                    }}>
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
                    :
                    null
                }
                <div style={{
                    flex: "1"
                }}>
                    <ReactFlowProvider>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            deleteKeyCode={null}
                            snapToGrid={true}
                            onNodeClick={(event:React.MouseEvent, node:any)=>setSelectedNodeData(node)}
                        >
                            <Background />
                        </ReactFlow>
                    </ReactFlowProvider>
                </div>
                {
                    selectedNode ?
                    <div style={{
                            display: "flex",
                            flexDirection: "column",
                            width: "400px"
                        }}
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
                                            selectedNodeRequirements.map((item:any) => {
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