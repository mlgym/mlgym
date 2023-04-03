import { Button, FormControlLabel, IconButton, LinearProgress, Skeleton, Switch, TextField, Toolbar } from '@mui/material';
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
import axios from 'axios';
import api from '../../../app/ApiMaster';
import { JsonViewer } from '@textea/json-viewer';

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

const JSON_DUMMY_DATA = {
    "id": 9,
    "title": "Infinix INBOOK",
    "description": "Infinix Inbook X1 Ci3 10th 8GB...",
    "price": 1099,
    "discountPercentage": 11.83,
    "rating": 4.54,
    "stock": 96,
    "brand": "Infinix",
    "category": "laptops",
    "thumbnail": "https://i.dummyjson.com/data/products/9/thumbnail.jpg",
    "images": [
      "https://i.dummyjson.com/data/products/9/1.jpg",
      "https://i.dummyjson.com/data/products/9/2.png",
      "https://i.dummyjson.com/data/products/9/3.png",
      "https://i.dummyjson.com/data/products/9/4.jpg",
      "https://i.dummyjson.com/data/products/9/thumbnail.jpg"
    ]
}

function ExperimentPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    let experiment_id = searchParams.get("experiment_id") as string;
    const [selectedExperiment, setSelectedExperiment] = useState(obj)
    const filteredExp = useAppSelector(state => selectRowById(state, experiment_id));
    const [showMore, setShowMore] = useState(false);
    const [loss_or_metric_data, setLossOrMetricData] = useState(obj);
    const [isLoadingCheckpointData, setIsLoadingCheckpointData] = useState(false);
    const [errorInCheckpointData, setErrorInCheckpointData] = useState("");
    const [checkpointId, setCheckpointId] = useState("");
    const [checkpointData, setCheckpointData] = useState(obj);
    const [configFileName, setConfigFileName] = useState("");
    const [configFileData, setConfigFileData] = useState(obj);
    const [isLoadingExpConfigFile, setIsLoadingExpConfigFile] = useState(false);
    const [errorInExpConfigFileData, setErrorInExpConfigFileData] = useState("");

    useEffect(() => {
        console.log("filteredExp: ",filteredExp);
        // setConfigFileData(JSON_DUMMY_DATA);
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
            setErrorInCheckpointData("");
        }
        else if (key === "configFileName") {
            setConfigFileName(text);
            setErrorInExpConfigFileData("");
        }
    }

    function get_checkpoint_data() {
        if (checkpointId && checkpointId.length > 0) {
        
            let checkpoint_url = api.checkpoint_url.replace("<grid_search_id>", "");
            let experiment_id = filteredExp?.experiment_id;
            if (experiment_id) {
                checkpoint_url = checkpoint_url.replace("<experiment_id>", experiment_id.toString());
            }
            checkpoint_url = checkpoint_url.replace("<checkpoint_id>", checkpointId);
            
            setErrorInCheckpointData("");            
            setIsLoadingCheckpointData(true);

            axios(checkpoint_url).then((data) => {
                console.log("Got get_checkpoint_data: ", data);
                setIsLoadingCheckpointData(false);
            })
            .catch((error) => {
                console.log("Error in get_checkpoint_data: ", error);
                setIsLoadingCheckpointData(false);
                setErrorInCheckpointData("Oops! something went wrong in getting checkpoint data");
            });
        }
        else {
            console.log("Please enter check point id");
        }
    }

    function get_experiment_config_file() {
        if (configFileName && configFileName.length > 0) {
            let experiment_config_file = api.experiment_config_file.replace("<grid_search_id>", "");
            let experiment_id = filteredExp?.experiment_id;
            if (experiment_id) {
                experiment_config_file = experiment_config_file.replace("<experiment_id>", experiment_id.toString());
            }
            experiment_config_file = experiment_config_file.replace("<config_file_name>", configFileName);
            
            setErrorInExpConfigFileData("");
            setIsLoadingExpConfigFile(true);

            axios(experiment_config_file).then((data) => {
                console.log("Got experiment_config_file: ", data);
                setIsLoadingExpConfigFile(false);
            })
            .catch((error) => {
                console.log("Error in experiment_config_file: ", error);
                setIsLoadingExpConfigFile(false);
                setErrorInExpConfigFileData("Oops! something went wrong in getting Experiment Config File");
            });   
        }
        else {
            console.log("Please enter config file name");
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
                                            {
                                                selectedExperiment.starting_time !== -1 ?
                                                moment(new Date(selectedExperiment.starting_time*1000)).format("YYYY-MM-DD hh:MM:SS")
                                                :
                                                "--"
                                            }
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
                                            selectedExperiment.hasOwnProperty("current_epoch") ?
                                            <HalfDonoughtGraph 
                                                graph_data={
                                                    [
                                                        selectedExperiment.current_epoch,
                                                        selectedExperiment.num_epochs-selectedExperiment.current_epoch
                                                    ]
                                                }
                                                label_data={
                                                    [
                                                        selectedExperiment.current_epoch+"%",
                                                        (selectedExperiment.num_epochs-selectedExperiment.current_epoch)+"%"
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
                            <Card className={styles.cardcontent_with_download_btn}>
                                <CardContent>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            <TextField
                                                error={errorInCheckpointData.length > 0}
                                                helperText={errorInCheckpointData.length > 0? errorInCheckpointData : ""}
                                                label="Enter Checkpoint Id" 
                                                variant="standard" 
                                                value={checkpointId}
                                                disabled={isLoadingCheckpointData}
                                                onChange={(e)=>changeText("checkpointId", e.target.value)}
                                            />
                                        </div>
                                        <div className={styles.cardcontent_value}>
                                            <IconButton 
                                                disabled={isLoadingCheckpointData || checkpointId.length === 0}
                                                size="large" 
                                                onClick={()=>get_checkpoint_data()}
                                            >
                                                <Send /> 
                                            </IconButton>
                                        </div>
                                    </div>
                                    {
                                        isLoadingCheckpointData ?
                                        <Box sx={{ width: '100%' }}>
                                            <LinearProgress />
                                        </Box>
                                        :
                                        !isLoadingCheckpointData && errorInCheckpointData.length > 0 ?
                                        null
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
                                                        <IconButton size="large" onClick={()=>get_checkpoint_data()}>
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        :
                                        null
                                    }
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item={true} xs={12} sm={12} md={9}>
                            <Card className={styles.card}>
                                <CardContent>
                                    <div className={styles.cardcontent}>
                                        <div className={styles.cardcontent_key}>
                                            <div className={styles.cardcontent}>
                                                <div className={styles.cardcontent_key}>
                                                    <TextField
                                                        error={errorInExpConfigFileData.length > 0}
                                                        helperText={errorInExpConfigFileData.length > 0? errorInExpConfigFileData : ""}
                                                        label="Enter Config File Name" 
                                                        variant="standard"
                                                        value={configFileName}
                                                        disabled={isLoadingExpConfigFile}
                                                        onChange={(e)=>changeText("configFileName", e.target.value)}
                                                    />
                                                </div>
                                                <div className={styles.cardcontent_value}>
                                                    <IconButton 
                                                        size="large"
                                                        disabled={isLoadingExpConfigFile ||configFileName.length === 0}
                                                        onClick={()=>get_experiment_config_file()}
                                                    >
                                                        <Send /> 
                                                    </IconButton>
                                                </div>
                                            </div>
                                        </div>
                                        {
                                            Object.keys(configFileData).length > 0 ?
                                            <div className={styles.cardcontent_key}>
                                                <div className={styles.cardcontent}>
                                                    <div className={styles.cardcontent_key}>
                                                        <IconButton 
                                                            size="large"
                                                            style={{ marginRight: "20px" }} 
                                                        >
                                                            <Download /> 
                                                        </IconButton>
                                                    </div>
                                                    <div className={styles.cardcontent_key}>
                                                        <FormControlLabel
                                                            sx={{
                                                                display: 'block',
                                                            }}
                                                            disabled={isLoadingExpConfigFile ||configFileName.length === 0}
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
                                            :
                                            null
                                        }
                                    </div>
                                    {
                                        isLoadingExpConfigFile ?
                                        <Box sx={{ width: '100%' }}>
                                            <LinearProgress />
                                        </Box>
                                        :
                                        !isLoadingExpConfigFile && errorInExpConfigFileData.length > 0 ?
                                        null
                                        :
                                        !isLoadingExpConfigFile && !configFileData ?
                                        <div>
                                            <JsonViewer value={configFileData} />
                                        </div>
                                        :
                                        null
                                    }
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