import Tree from 'react-d3-tree';
import { useEffect, useState } from 'react';
import { RawNodeDatum } from 'react-d3-tree';
import { Grid } from '@mui/material';
import styles from './DatasetDetails.module.css';
import { AnyKeyValuePairs } from '../../../app/interfaces';


export default function DatasetDetails({ datasetDetails }: { datasetDetails: AnyKeyValuePairs }) {

    const [treeData, setTreeData] = useState<RawNodeDatum>({ name: '' });

    useEffect(() => {
        if (datasetDetails.dataset_splits) {

            const split_config = datasetDetails.dataset_splits.split_config;
            let split_children: { name: any, children: any }[] = [];

            for (const split_config_key in split_config) {

                let splits_percentage = datasetDetails.dataset_splits.splits_percentage;
                let split_children_children: { name: any }[] = [];

                if (splits_percentage[split_config[split_config_key].split]) {
                    const p = splits_percentage[split_config[split_config_key].split];
                    for (const k in p) {
                        let split_child_child_obj = {
                            name: k,
                            attributes: {
                                percentage: (p[k] * 100).toString() + "%",
                            },
                        }
                        split_children_children.push(split_child_child_obj);
                    }

                }
                let split_child_obj = {
                    name: split_config[split_config_key].split,
                    children: split_children_children
                }
                split_children.push(split_child_obj);
            }

            const myTreeData = {
                name: "Dataset",
                attributes: {
                    name: datasetDetails.considered_dataset,
                },
                children: split_children
            };
            setTreeData(myTreeData);
        }

    }, [datasetDetails])

    return (
        <Grid container>
            {
                datasetDetails.label_distribution === "" ?
                    null
                    :
                    <Grid item={true} xs={12} sm={12} md={12} lg={12} className={styles.label_dist_container}>
                        <div className={styles.label_dist_header}>
                            Label Distribution:
                        </div>
                        <div className={styles.label_dist_text}>
                            {datasetDetails.label_distribution}
                        </div>
                    </Grid>
            }
            <Grid item={true} xs={12} sm={12} md={12} lg={12} className={styles.tree_container}>
                <Tree
                    data={treeData}
                    pathFunc="diagonal"
                    enableLegacyTransitions={true}
                    translate={{ x: 200, y: 120 }}
                />
            </Grid>
        </Grid>
    )
}

// ASK: is this file deprecated?