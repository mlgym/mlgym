import styles from '../ExperimentPage.module.css';
import { Card, CardContent, Grid } from '@mui/material';
import moment from 'moment';
import { useState } from 'react';
import { AnyKeyValuePairsInterface } from '../ExperimentPage';
import { CardDetails } from './CardDetails';

export function ExperimentDetails({selectedExperiment} : {selectedExperiment: AnyKeyValuePairsInterface}) {
    
    const [showMore, setShowMore] = useState(false);

    return(
        <>
            <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails
                        cardTitle='Overview'
                        contentObj={
                            {   
                                "Experiment ID": selectedExperiment.experiment_id,
                                "Job Type": 
                                selectedExperiment.job_type ?
                                selectedExperiment.job_type
                                :
                                "--",
                                "Device":
                                selectedExperiment.device ? 
                                selectedExperiment.device
                                :
                                "--"
                            }
                        }
                    />
                </Grid>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails 
                        cardTitle='Times'
                        contentObj={
                            {   
                                "Start": selectedExperiment.starting_time && selectedExperiment.starting_time !== -1 ?
                                moment(new Date(selectedExperiment.starting_time*1000)).format("YYYY-MM-DD hh:MM:SS")
                                :
                                "--",
                                "End": selectedExperiment.finishing_time && selectedExperiment.finishing_time !== -1 ?
                                moment(new Date(selectedExperiment.finishing_time*1000)).format("YYYY-MM-DD hh:MM:SS")
                                :
                                "--"
                            }
                        }
                    />
                </Grid>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails 
                        cardTitle='State'
                        contentObj={
                            {   
                                "Job Status": 
                                selectedExperiment.hasOwnProperty("error") && selectedExperiment.error !== null ?
                                "FAILED"
                                :
                                selectedExperiment.job_status === "DONE" ?
                                "COMPLETED"
                                :
                                selectedExperiment.job_status === "INIT" ?
                                "INITIALIZING"
                                :
                                selectedExperiment.job_status ?
                                selectedExperiment.job_status
                                :
                                "--",
                                "Model Status": 
                                selectedExperiment.model_status ?
                                selectedExperiment.model_status 
                                :
                                "--"
                            }
                        }
                    />
                </Grid>
            </Grid>
            {
                selectedExperiment.hasOwnProperty("error") && selectedExperiment.error !== null ?
                <div className={styles.error_card}>
                    <Card className={styles.card}>
                        <CardContent>
                            <div className={styles.card_content_typography_error} >
                                Error
                            </div>
                            <div className={styles.cardcontent_key}>
                                {selectedExperiment.error}
                            </div>
                            {
                                selectedExperiment.hasOwnProperty("stacktrace") && selectedExperiment.stacktrace !== (null||undefined) ?
                                <div>
                                    <br/>
                                    <div className={styles.card_content_typography} >
                                        Stacktrace
                                    </div>
                                    <div className={styles.cardcontent_key}>
                                        {
                                            showMore ? 
                                            selectedExperiment.stacktrace 
                                            : 
                                            selectedExperiment.stacktrace.substring(0,100)+"..."
                                        }
                                        <span 
                                            onClick={()=>setShowMore(!showMore)} 
                                            className={styles.show_more_text}
                                        >
                                            {
                                                showMore ? "show less" : "show more"
                                            }
                                        </span>
                                    </div>
                                </div>
                                :
                                null
                            }
                        </CardContent>
                    </Card>
                </div>
                :
                null
            }
        </>
    );
}
