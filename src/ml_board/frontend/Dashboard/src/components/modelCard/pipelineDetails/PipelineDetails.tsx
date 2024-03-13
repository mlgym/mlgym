import { AnyKeyValuePairsInterface } from '../../experimentPage/ExperimentPage';
import Tree from 'react-d3-tree';
import { SyntheticEvent, useEffect, useState } from 'react';
import { HierarchyPointNode } from 'd3';
import { RawNodeDatum, TreeNodeDatum } from 'react-d3-tree';
import { Grid } from '@mui/material';
import styles from './PipelineDetails.module.css';
import { JsonViewer } from '@textea/json-viewer';

var treeDataObj: RawNodeDatum = {
    name: ''
}

export default function PipelineDetails({pipelineDetails, experiment_id, treeOrientationProp} : {pipelineDetails: AnyKeyValuePairsInterface, experiment_id: string, treeOrientationProp: any}) {

    const [treeData, setTreeData] = useState(treeDataObj);
    const [clickedNode, setNodeClick] = useState<any>(null);

    function tree_children_iterator(obj: any) {
        let children: { name: any, attribute?: any, children?: any } [] = [];
        if (typeof obj === 'object' && obj !== null) {
            for(const key in obj) {
                if(key !== 'requirements') {
                    if(typeof obj[key] === 'object' && obj[key] !== null) {
                        let tree_children = tree_children_iterator(obj[key].nodes)
                        let child_obj = {
                            name: key,
                            children: tree_children,
                            config: JSON.parse(obj[key].config_str)
                        }
                        children.push(child_obj);
                    }
                    else {
                        let child_obj = {
                            name: key,
                            attributes: {
                                value: obj[key]
                            }
                        }
                        children.push(child_obj);
                    }
                }
            }
            return children
        }
        else {
            let child_non_obj = {
                name: obj
            }
            children.push(child_non_obj);
        }
    }

    useEffect(() => {
        if(pipelineDetails && Object.keys(pipelineDetails).length > 0) {
            
            console.log("pipelineDetails: ",pipelineDetails)
            
            let tree_data = tree_children_iterator(pipelineDetails);
            // console.log("tree_data: ",tree_data)

            const myTreeData = {
                name: "Experiment_Pipeline",
                attributes: {
                    name: "Experiment "+experiment_id.toString(),
                },
                children: tree_data
            }
            // console.log("myTreeData: ",myTreeData)

            setTreeData(myTreeData);
        }
    }, [pipelineDetails])
    
    function filterKeys(obj: any): any {
        if (typeof obj !== 'object' || obj === null) {
          return obj;
        }
      
        if (Array.isArray(obj)) {
          return obj.map(filterKeys);
        }
      
        const filteredObj: any = {};
      
        for (const key in obj) {
          if (key === 'config' || key === 'children' || key === 'name' || key === 'attributes') {
            if(key === 'children') {
                filteredObj[key] = filterKeys(obj[key]);
            }
            else {
                filteredObj[key] = obj[key]
            }
          }
        }
        // console.log('Node filteredObj:', filteredObj);
      
        return filteredObj;
    }

    function handleNodeClick(nodeData: HierarchyPointNode<TreeNodeDatum>, e: SyntheticEvent) {
        // Perform your custom actions here based on the clicked nodeData
        // console.log('Node clicked:', nodeData);
        let filteredData = filterKeys(nodeData.data);
        let selectedNodeData = {
            children: filteredData.children,
            config: filteredData.config,
            name: filteredData.name,
            depth: nodeData.depth,
            height: nodeData.height,
            parent: nodeData.parent ? filterKeys(nodeData.parent.data) : null
        }
        // console.log('Selected Node Data:', selectedNodeData);
        setNodeClick(selectedNodeData);
    }

    return(
        <Grid container>
            <Grid item={true} xs={12} sm={12} md={8} lg={8} >
                <div id="pipeline_graph_component" className={styles.tree_container}>
                    <Tree
                        data={treeData}
                        initialDepth={1}
                        pathFunc="diagonal"
                        orientation={treeOrientationProp}
                        separation={{ siblings: 1, nonSiblings: 1.5 }}
                        enableLegacyTransitions={true}
                        translate={{ x: window.innerWidth/4, y: window.innerHeight/2 }}
                        onNodeClick={(node: HierarchyPointNode<TreeNodeDatum>, e: SyntheticEvent)=>handleNodeClick(node, e)}
                    />
                </div>
            </Grid>
            <Grid item={true} xs={12} sm={12} md={4} lg={4}>
                <div className={styles.config_container}>
                    <h4>Config: {clickedNode ? clickedNode.name : "no node selected"}</h4>
                </div>
                <div>
                    {clickedNode && <JsonViewer value={clickedNode}/>}
                </div>
            </Grid>
      </Grid>
    )
}
