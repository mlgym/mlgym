import styles from '../ExperimentPage.module.css';
import { Card, CardContent, Grid } from '@mui/material';
import moment from 'moment';
import { useState } from 'react';
import { AnyKeyValuePairsInterface } from '../ExperimentPage';
import { CardDetails } from './CardDetails';

interface return_obj_interface {
    [key:string]: string
}
export function ExperimentDetails({selectedExperiment} : {selectedExperiment: AnyKeyValuePairsInterface}) {
    
    const [showMore, setShowMore] = useState(false);

    function conditional_render_exp_overview() {
        let return_obj:return_obj_interface = {};
        return_obj["Experiment ID"] = selectedExperiment.experiment_id;

        if(selectedExperiment.job_type) {
            return_obj["Job Type"] = selectedExperiment.job_type;
        }
        else {
            return_obj["Job Type"] = "--";
        }

        if(selectedExperiment.device) {
            return_obj["Device"] = selectedExperiment.device;
        }
        else {
            return_obj["Device"] = "--";
        }

        return return_obj;
    }

    function conditional_render_exp_state() {
        let return_obj:return_obj_interface = {};

        if(selectedExperiment.hasOwnProperty("error") && selectedExperiment.error !== null) {
            return_obj["Job Status"] = "FAILED";
        }
        else if(selectedExperiment.job_status === "DONE") {
            return_obj["Job Status"] = "COMPLETED";
        }
        else if(selectedExperiment.job_status === "INIT") {
            return_obj["Job Status"] = "INITIALIZING";
        }
        else if(selectedExperiment.job_status) {
            return_obj["Job Status"] = selectedExperiment.job_status;
        }
        else {
            return_obj["Job Status"] = "--";
        }

        if(selectedExperiment.model_status) {
            return_obj["Model Status"] = selectedExperiment.model_status;
        }
        else {
            return_obj["Model Status"] = "--";
        }

        return return_obj;
    }

    function conditional_render_exp_date_time() {
        let return_obj:return_obj_interface = {};

        if(selectedExperiment.starting_time && selectedExperiment.starting_time !== -1) {
            return_obj["Start"] = moment(new Date(selectedExperiment.starting_time * 1000)).format("YYYY-MM-DD hh:MM:SS");
        }
        else {
            return_obj["Start"] = "--";
        }

        if(selectedExperiment.finishing_time && selectedExperiment.finishing_time !== -1) {
            return_obj["End"] = moment(new Date(selectedExperiment.finishing_time * 1000)).format("YYYY-MM-DD hh:MM:SS");
        }
        else {
            return_obj["End"] = "--";
        }

        return return_obj;
    }
    
    return(
        <>
            <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails
                        cardTitle='Overview'
                        contentObj={conditional_render_exp_overview()}
                    />
                </Grid>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails
                        cardTitle='Times'
                        contentObj={conditional_render_exp_date_time()}
                    />
                </Grid>
                <Grid item={true} xs={12} sm={12} md={4}>
                    <CardDetails
                        cardTitle='State'
                        contentObj={conditional_render_exp_state()}
                    />
                </Grid>
            </Grid>
            {
                selectedExperiment.error && <div className={styles.error_card}>
                    <Card className={styles.card}>
                        <CardContent>
                            <div className={styles.card_content_typography_error} >
                                Error
                            </div>
                            <div className={styles.cardcontent_key}>
                                {selectedExperiment.error}
                            </div>
                            {
                                selectedExperiment.stacktrace && <div>
                                    <br />
                                    <div className={styles.card_content_typography} >
                                        Stacktrace
                                    </div>
                                    <div className={styles.cardcontent_key}>
                                        {
                                            showMore ?
                                                selectedExperiment.stacktrace
                                                :
                                                selectedExperiment.stacktrace.substring(0, 100) + "..."
                                        }
                                        <span
                                            onClick={() => setShowMore(!showMore)}
                                            className={styles.show_more_text}
                                        >
                                            {
                                                showMore ? "show less" : "show more"
                                            }
                                        </span>
                                    </div>
                                </div>
                            }
                        </CardContent>
                    </Card>
                </div>
            }
        </>
    );
}
