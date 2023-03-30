import { Button, FormControlLabel, IconButton, Skeleton, Switch, TextField, Toolbar } from '@mui/material';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppSelector } from "../../../app/hooks";
import { selectRowById } from '../../../redux/table/tableSlice';
import HalfDonoughtGraph from '../graphs/HalfDonoughtGraph';
import { styled } from '@mui/material/styles';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import MuiAccordion, { AccordionProps } from '@mui/material/Accordion';
import MuiAccordionSummary, {
  AccordionSummaryProps,
} from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import styles from './ExperimentPage.module.css';
import styles_graphs from "../../graphs/Graphs.module.css";
import moment from 'moment';
import LineGraph from '../graphs/LineGraph';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { getRandomColor } from '../../../worker_socket/event_handlers/evaluationResultDataHandler';
import { Download } from '@mui/icons-material';
import Send from '@mui/icons-material/Send';
import DoNotDisturbAltIcon from '@mui/icons-material/DoNotDisturbAlt';
import DescriptionIcon from '@mui/icons-material/Description';

interface expObj {
    [key: string]: any
}
var obj: expObj = {}

const Accordion = styled((props: AccordionProps) => (
    <MuiAccordion disableGutters elevation={0} square {...props} />))(() => ({
    '&:not(:last-child)': {
        borderBottom: 0,
    },
    '&:before': {
        display: 'none',
    }
}));
  
const AccordionSummary = styled((props: AccordionSummaryProps) => (
    <MuiAccordionSummary
      expandIcon={<ArrowForwardIosSharpIcon className={styles.expand_more_icon} />}
      {...props}
    />
  ))(({ theme }) => ({
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
      transform: 'rotate(90deg)',
    },
    '& .MuiAccordionSummary-content': {
      marginLeft: theme.spacing(1),
    },
}));
  
const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
    paddingTop: theme.spacing(0),
    // borderTop: '1px solid rgba(0, 0, 0, .125)',
}));

interface loss_or_metric_interface {
    [key: string]: Array<{
        exp_id: number,
        label: string,
        data: Array<number>,
        fill: Boolean,
        backgroundColor: string,
        borderColor: string,
        tension: number,
        pointRadius: Number,
        pointHitRadius: Number,
        pointHoverRadius: Number
    }>
}

function ExperimentPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    let experiment_id = searchParams.get("experiment_id") as string;
    const [selectedExperiment, setSelectedExperiment] = useState(obj)
    const filteredExp = useAppSelector(state => selectRowById(state, experiment_id));
    const [showMore, setShowMore] = useState(false);
    const [loss_or_metric_data, setLossOrMetricData] = useState(obj);
    const [isLoadingCheckpointData, setIsLoadingCheckpointData] = useState(false);
    const [isErrorInCheckpointData, setIsErrorInCheckpointData] = useState(false);
    const [checkpointId, setCheckpointId] = useState("");
    const [checkpointData, setCheckpointData] = useState(obj);
    const [configFileName, setConfigFileName] = useState("");
    const [configFileData, setConfigFileData] = useState(obj);

    useEffect(() => {
        console.log("filteredExp: ",filteredExp);
        if (filteredExp) {
            setSelectedExperiment(filteredExp);
            let loss_or_metric:loss_or_metric_interface = {};
            // TODO: replace any type with the interface of filteredExp (i.e <Row> as defined in redux)
            let selectedExp:any = filteredExp;
            if (selectedExp.splits) {
                let split_arrays = selectedExp.splits.split(",");
                split_arrays.map((split_type:string) => {
                    Object.keys(selectedExp).map((key) => {
                        if (key.includes(split_type)) {
                            let color = getRandomColor();
                            loss_or_metric[key] = [{
                                exp_id: selectedExp.experiment_id,
                                label: "experiment_"+selectedExp.experiment_id,
                                // TODO: replace this::[selectedExp[key]] with selectedExp[key]
                                data: [selectedExp[key]],
                                fill: false,
                                backgroundColor: color,
                                borderColor: color,
                                tension: 0,
                                pointRadius: 3,
                                pointHitRadius: 20,
                                pointHoverRadius: 12
                            }];
                        }
                    });
                });
                console.log("loss_or_metric: ",loss_or_metric);
                setLossOrMetricData(loss_or_metric);
            }
            
        }
    },[filteredExp])

    function changeText(key:string, text:string) {
        if (key === "checkpointId") {
            setCheckpointId(text);            
        }
        else if (key === "configFileName") {
            setConfigFileName(text);
        }
    }

    return(
        <div className={styles.main}>
            <Toolbar />
            <Accordion defaultExpanded={true}>
                <AccordionSummary>
                    <div className={styles.accordian_heading}>Details</div>
                </AccordionSummary>
                <AccordionDetails className={styles.accordian_details}>
                    <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
                        <Grid item={true} xs={12} sm={12} md={4}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.card_content_typography}>
                                        Overview
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Experiment ID
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {selectedExperiment.experiment_id}
                                        </div>
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Job Type
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {selectedExperiment.job_type}
                                        </div>
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Device
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {selectedExperiment.device}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item={true} xs={12} sm={12} md={4}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.card_content_typography}>
                                        Times
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Start
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {moment(new Date(selectedExperiment.starting_time*1000)).format("YYYY-MM-DD hh:MM:SS")}
                                        </div>
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            End
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {
                                                selectedExperiment.finishing_time !== -1 ?
                                                moment(new Date(selectedExperiment.finishing_time*1000)).format("YYYY-MM-DD hh:MM:SS")
                                                :
                                                "--"
                                            }
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item={true} xs={12} sm={12} md={4}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.card_content_typography}>
                                    State
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Job Status
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                        {
                                            selectedExperiment.hasOwnProperty("error") && selectedExperiment.error !== null ?
                                            "FAILED"
                                            :
                                            selectedExperiment.job_status === "DONE" ?
                                            "COMPLETED"
                                            :
                                            selectedExperiment.job_status === "INIT" ?
                                            "INITIALIZING"
                                            :
                                            selectedExperiment.job_status
                                        }
                                        </div>
                                    </div>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            Model Status
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            {
                                                selectedExperiment.model_status ?
                                                selectedExperiment.model_status 
                                                :
                                                "--"
                                            }
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
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
                </AccordionDetails>
            </Accordion>
            <Accordion defaultExpanded={true}>
                <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
                    <div className={styles.accordian_heading}>Progress</div>
                </AccordionSummary>
                <AccordionDetails>
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
                                            selectedExperiment.hasOwnProperty("epoch_progress") && selectedExperiment.epoch_progress ?
                                            <HalfDonoughtGraph 
                                                graph_data={
                                                    [
                                                        selectedExperiment.epoch_progress,
                                                        1-selectedExperiment.epoch_progress
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
                </AccordionDetails>
            </Accordion>
            <Accordion defaultExpanded={true}>
                <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
                    <div className={styles.accordian_heading}>Configurations</div>
                </AccordionSummary>
                <AccordionDetails>
                    <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
                        <Grid item={true} xs={12} sm={12} md={3}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            <TextField
                                                label="Enter Checkpoint Id" 
                                                variant="standard" 
                                                value={checkpointId}
                                                onChange={(e)=>changeText("checkpointId", e.target.value)}
                                            />
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            <IconButton size="large">
                                                <Send /> 
                                            </IconButton>
                                        </div>
                                    </div>
                                    <br/>
                                    {
                                        isLoadingCheckpointData ?
                                        <div>
                                            <Skeleton animation="wave" height={60} />
                                            <Skeleton animation="wave" height={60} />
                                            <Skeleton animation="wave" height={60} />
                                            <Skeleton animation="wave" height={60} />
                                        </div>
                                        :
                                        !isLoadingCheckpointData && isErrorInCheckpointData ?
                                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                                            <DoNotDisturbAltIcon style={{ height: '200px', width: '200px'}}/>
                                            <h3>No Data Available</h3>
                                        </div>
                                        :
                                        !isLoadingCheckpointData && !checkpointData ?
                                        <div>
                                            <div>
                                                <div className={styles.cardcontent}>
                                                    <div className={styles.cardcontent_key}>
                                                        Model
                                                    </div>
                                                    <div className={styles.cardcontent_value}>
                                                        <IconButton size="large">
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                </div>
                                                <div className={styles.cardcontent}>
                                                    <div className={styles.cardcontent_key}>
                                                        Optimizer
                                                    </div>
                                                    <div className={styles.cardcontent_value}>
                                                        <IconButton size="large">
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                </div>
                                                <div className={styles.cardcontent}>
                                                    <div className={styles.cardcontent_key}>
                                                        Stateful Components
                                                    </div>
                                                    <div className={styles.cardcontent_value}>
                                                        <IconButton size="large">
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                </div>
                                                <div className={styles.cardcontent}>
                                                    <div className={styles.cardcontent_key}>
                                                        LR Scheduler
                                                    </div>
                                                    <div className={styles.cardcontent_value}>
                                                        <IconButton size="large">
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        :
                                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                                            <DescriptionIcon style={{ height: '200px', width: '200px'}}/>
                                            <h3>Enter Checkpoint Id</h3>
                                        </div>
                                    }
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item={true} xs={12} sm={12} md={9}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key} style={{ width: "80%"}}>
                                            <div className={styles.cardcontent}>
                                                <div className={styles.cardcontent_key}>
                                                    <TextField
                                                        label="Enter Config File Name" 
                                                        variant="standard"
                                                        style={{ width: "800px" }}
                                                        value={configFileName}
                                                        onChange={(e)=>changeText("configFileName", e.target.value)}
                                                    />
                                                </div>
                                                <div className={styles.cardcontent_value}>
                                                    <IconButton size="large">
                                                        <Send /> 
                                                    </IconButton>
                                                </div>
                                            </div>
                                        </div>

                                        <div className={styles.cardcontent_key} style={{ width: "20%" }}>
                                            <div className={styles.cardcontent}>
                                                <div className={styles.cardcontent_key}>
                                                    <IconButton size="large" style={{ marginRight: "20px" }}>
                                                        <Download /> 
                                                    </IconButton>
                                                </div>
                                                <div className={styles.cardcontent_key}>
                                                    <FormControlLabel
                                                        sx={{
                                                            display: 'block',
                                                        }}
                                                        control={
                                                        <Switch
                                                            checked={true}
                                                            // onChange={() => setLoading(!loading)}
                                                            name="loading"
                                                            color="primary"
                                                        />
                                                        }
                                                        label="View / Hide"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ marginTop: "-80px" }}>
                                        <Skeleton animation="wave" height={400} />
                                    </div>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </AccordionDetails>
            </Accordion>
            <Accordion defaultExpanded={true}>
                <AccordionSummary>
                    <div className={styles.accordian_heading}>Losses & Metrics</div>
                </AccordionSummary>
                <AccordionDetails>
                    {
                        Object.keys(loss_or_metric_data).length > 0 ?
                        <Grid container rowSpacing={1} spacing={{ xs: 2, md: 3 }} className={styles_graphs.grid_container}>
                            {
                                Object.keys(loss_or_metric_data).map((loss_or_metric_key, index) => {
                                    return(
                                        <Grid item={true} xs={12} sm={12} md={6} key={index}>
                                            <Card className={styles_graphs.grid_card}>
                                                <Box className={styles_graphs.graphs_chart_container}>
                                                    <LineGraph
                                                        graph_data={loss_or_metric_data[loss_or_metric_key]}
                                                        title_text={loss_or_metric_key.split("_").join(" ")}
                                                    />
                                                </Box>
                                            </Card>
                                        </Grid>
                                    )
                                })
                            }
                        </Grid>
                        :
                        <Box className={styles_graphs.no_data_to_viz}>
                            --- No Data To Visualize ---
                        </Box>
                    }
                </AccordionDetails>
            </Accordion>
        </div>
    )
}

export default ExperimentPage;