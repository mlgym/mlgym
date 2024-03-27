import styles from '../ExperimentPage.module.css';
import { Card, CardContent, Grid } from '@mui/material';
import HalfDonoughtGraph from '../HalfDonoughtGraph/HalfDonoughtGraph';
import { AnyKeyValuePairs } from '../../../app/interfaces';

export function ExperimentProgress({selectedExperiment} : {selectedExperiment: AnyKeyValuePairs }) {

    return (
        <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
            <Grid item={true} xs={12} sm={12} md={6}>
                <Card className={styles.card}>
                    <CardContent>
                        <div className={styles.card_content_typography} >
                            <div className={styles.cardcontent_typography}>
                                <div>
                                    Epoch Details: 
                                </div>
                                {
                                    selectedExperiment.hasOwnProperty("current_epoch") && selectedExperiment.hasOwnProperty("num_epochs") ?
                                    <div>
                                        {selectedExperiment.current_epoch} / {selectedExperiment.num_epochs}
                                    </div>
                                    :
                                    <div>--</div>
                                }
                            </div>
                        </div>
                        <div className={styles.donought_container}>
                            {
                                selectedExperiment.hasOwnProperty("current_epoch") ?
                                <HalfDonoughtGraph 
                                    graph_data={
                                        [
                                            selectedExperiment.epoch_progress,
                                            (1-selectedExperiment.epoch_progress)
                                        ]
                                    }
                                    label_data={
                                        [
                                            selectedExperiment.epoch_progress*100+"%",
                                            (1-selectedExperiment.epoch_progress)*100+"%"
                                        ]
                                    }
                                />
                                :
                                <HalfDonoughtGraph 
                                    graph_data={[0,100]}
                                    label_data={["--","--"]}
                                />
                            }
                        </div>
                    </CardContent>
                </Card>
            </Grid>
            <Grid item={true} xs={12} sm={12} md={6}>
                <Card className={styles.card}>
                    <CardContent>
                        <div className={styles.card_content_typography} >
                            <div className={styles.cardcontent_typography}>
                                <div>
                                    Batch Details: 
                                </div>
                                {
                                    selectedExperiment.hasOwnProperty("current_batch") && selectedExperiment.hasOwnProperty("num_batches") ?
                                    <div>
                                        {selectedExperiment.current_batch} / {selectedExperiment.num_batches}
                                    </div>
                                    :
                                    <div>--</div>
                                }
                            </div>
                        </div>
                        <div className={styles.donought_container}>
                            {
                                selectedExperiment.hasOwnProperty("batch_progress") && selectedExperiment.batch_progress ?
                                <HalfDonoughtGraph
                                    graph_data={
                                        [
                                            selectedExperiment.batch_progress,
                                            1-selectedExperiment.batch_progress
                                        ]
                                    }
                                    label_data={
                                        [
                                            selectedExperiment.batch_progress*100+"%",
                                            (1-selectedExperiment.batch_progress)*100+"%"
                                        ]
                                    }
                                />
                                :
                                <HalfDonoughtGraph 
                                    graph_data={[0,100]}
                                    label_data={["--","--"]}
                                />
                            }
                        </div>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
}