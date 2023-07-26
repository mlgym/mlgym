import { AnyKeyValuePairsInterface } from '../../experimentPage/ExperimentPage';
import Tree from 'react-d3-tree';
import { useEffect, useState } from 'react';
import { RawNodeDatum } from 'react-d3-tree';
import { Grid } from '@mui/material';
import styles from './PipelineDetails.module.css';

var treeDataObj: RawNodeDatum = {
    name: ''
}

export default function PipelineDetails({pipelineDetails, experiment_id, treeOrientationProp} : {pipelineDetails: AnyKeyValuePairsInterface, experiment_id: string, treeOrientationProp: any}) {

    const [treeData, setTreeData] = useState(treeDataObj);

    function tree_children_iterator(obj: any) {
        let children: { name: any, attribute?: any, children?: any } [] = [];
        if (typeof obj === 'object' && obj !== null) {
            for(const key in obj) {
                if(typeof obj[key] === 'object' && obj[key] !== null) {
                    let tree_children = tree_children_iterator(obj[key])
                    let child_obj = {
                        name: key,
                        children: tree_children
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
            console.log("tree_data: ",tree_data)

            const myTreeData = {
                name: "Experiment_Pipeline",
                attributes: {
                    name: "Experiment "+experiment_id.toString(),
                },
                children: tree_data
            }
            console.log("myTreeData: ",myTreeData)

            setTreeData(myTreeData);
        }
    }, [pipelineDetails])

    return(
        <Grid container>
            <Grid item={true} xs={12} sm={12} md={12} lg={12} className={styles.tree_container}>
                <Tree
                    data={treeData}
                    initialDepth={1}
                    pathFunc="diagonal"
                    orientation={treeOrientationProp}
                    separation={{ siblings: 1, nonSiblings: 1.5 }}
                    enableLegacyTransitions={true}
                    translate={{ x: window.innerWidth/2 - 80, y: 150 }}
                />
            </Grid>
      </Grid>
    )
}
