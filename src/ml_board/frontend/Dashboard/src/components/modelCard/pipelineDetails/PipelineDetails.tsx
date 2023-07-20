import { AnyKeyValuePairsInterface } from '../../experimentPage/ExperimentPage';
import Tree from 'react-d3-tree';
import { useEffect, useState } from 'react';
import { RawNodeDatum } from 'react-d3-tree';
import { Grid } from '@mui/material';
import styles from './PipelineDetails.module.css';

var treeDataObj: RawNodeDatum = {
    name: ''
}

export default function PipelineDetails({pipelineDetails, experiment_id} : {pipelineDetails: AnyKeyValuePairsInterface, experiment_id: string}) {

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

    // function renderNodeWithCustomEvents(a: any) {
    //     return(
    //         <g>
    //             <foreignObject x="0" height="120px" width="500px" y="-60px">
    //                 <div
    //                     title={"Hi"}
    //                     className="elemental-node"
    //                     // style={a.nodeDatum.style}
    //                 >
    //                 <span title={"FN"} className="elemental-name">
    //                     {"SN"}
    //                 </span>
    //                 {/* {a.nodeDatum.fullName === false && (
    //                     <div className="elemental-node--hover">
    //                         <span>{a.nodeDatum.fullName}</span>
    //                     </div>
    //                 )} */}
    //                 </div>
    //             </foreignObject>
    //         </g>
    //     )
    // }

    return(
        <Grid container>
            <Grid item={true} xs={12} sm={12} md={12} lg={12} className={styles.tree_container}>
                <Tree
                    data={treeData}
                    // renderCustomNodeElement={(rd3tProps) =>
                    //     renderNodeWithCustomEvents({ ...rd3tProps })
                    // }
                    pathFunc="diagonal"
                    orientation="horizontal"
                    separation={{ siblings: 1, nonSiblings: 1.5 }}
                    enableLegacyTransitions={true}
                    translate={{ x: 200, y: 180 }}
                />
            </Grid>
      </Grid>
    )
}
