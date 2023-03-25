import { Toolbar } from '@mui/material';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppSelector } from "../../../app/hooks";
import { selectAllRows } from '../../../redux/table/tableSlice';
import { TableRow } from '../Dashboard';
import HalfDonoughtGraph from '../graphs/HalfDonoughtGraph';
import { CategoryScale, Chart as ChartJS, Filler, LinearScale, LineElement, PointElement, Title, ArcElement, Tooltip, Legend } from 'chart.js';
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
import { useSelector } from 'react-redux';
import LineGraph from '../graphs/LineGraph';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    ArcElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)
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
  
function ExperimentPage() {

    const [selectedExperiment, setSelectedExperiment] = useState(obj)
    const [searchParams, setSearchParams] = useSearchParams();
    const allTableRows = useAppSelector(selectAllRows);
    const [showMore, setShowMore] = useState(false);
    const [experiment_training_data, setExperimentTrainingData] = useState(obj)

    useEffect(() => {
        let experiment_id = searchParams.get("experiment_id");
        if (experiment_id !== null) {
            let filteredExp = allTableRows.filter(row => {
                return row.experiment_id === Number(experiment_id);
            })[0];
            console.log("filteredExp: ",filteredExp)
            if (filteredExp) {
                setSelectedExperiment(filteredExp);
            }
        }
    },[])

    return(
        <div className={styles.main}>
            <Toolbar />
            {/* <div className={styles.main_heading}>
                Experiment: {selectedExperiment.experiment_id}
            </div> */}
            <Accordion defaultExpanded={true}>
                <AccordionSummary>
                    <div className={styles.accordian_heading}>Details</div>
                </AccordionSummary>
                <AccordionDetails className={styles.accordian_details}>
                    <div className={styles.cardview}>
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
                                        {moment(new Date(selectedExperiment.starting_time)).format("YYYY-MM-DD hh:MM:SS")}
                                    </div>
                                </div>
                                <div className={styles.cardcontent}>
                                    <div className={styles.cardcontent_key}>
                                        End
                                    </div>
                                    <div className={styles.cardcontent_value}>
                                        {
                                            selectedExperiment.finishing_time !== -1 ?
                                            moment(new Date(selectedExperiment.finishing_time)).format("YYYY-MM-DD hh:MM:SS")
                                            :
                                            "--"
                                        }
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
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
                    </div>
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
                    <div className={styles.cardview}>
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
                    </div>
                </AccordionDetails>
            </Accordion>
            <Accordion defaultExpanded={true}>
                <AccordionSummary>
                    <div className={styles.accordian_heading}>Losses & Metrics</div>
                </AccordionSummary>
                <AccordionDetails>
                    {
                        Object.keys(experiment_training_data).length > 0 ?
                        <Grid container rowSpacing={1} spacing={{ xs: 2, md: 3 }} className={styles_graphs.grid_container}>
                            {
                                Object.keys(experiment_training_data).map((loss_or_metric, index) => {
                                    return(
                                        <Grid item={true} xs={12} sm={12} md={6} key={index}>
                                            <Card className={styles_graphs.grid_card}>
                                                <Box className={styles_graphs.graphs_chart_container}>
                                                    <LineGraph
                                                        graph_labels={experiment_training_data[loss_or_metric].labels}
                                                        graph_data={experiment_training_data[loss_or_metric].data}
                                                        title_text={loss_or_metric}
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