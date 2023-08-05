import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppSelector } from "../../app/hooks";
import { selectChartsByExperimentId } from '../../redux/charts/chartsSlice';
import { isConnected } from "../../redux/globalConfig/globalConfigSlice";
import { selectRowById } from '../../redux/table/tableSlice';
import Graph from "../graphs/Graph";
import CheckpointConfigurations from './CheckpointConfigurations/CheckpointConfigurations';
import ExperimentConfigurations from './ExperimentConfigurations/ExperimentConfigurations';
import EnvironmentDetails from '../modelCard/environmentDetails/EnvironmentDetails';
import { ExperimentDetails } from './ExperimentDetails/ExperimentDetails';
import { ExperimentProgress } from './ExperimentProgress/ExperimentProgress';
import { RoutesMapping } from '../../app/RoutesMapping';
// mui components & styles
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { styled, AccordionProps, AccordionSummaryProps, Box, Grid, Button } from '@mui/material';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import styles_graphs from "../graphs/Graphs.module.css";
import styles from './ExperimentPage.module.css';

export interface AnyKeyValuePairsInterface {
    [key: string]: any
}
var anyObj: AnyKeyValuePairsInterface = {}

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
}));

// TODO: FIX this rerenders CRAZY with every ping update !!!
function ExperimentPage() {
    
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    let experiment_id = searchParams.get("experiment_id") as string;
    const [selectedExperiment, setSelectedExperiment] = useState(anyObj)
    const filteredExp = useAppSelector(state => selectRowById(state, experiment_id));
    const selectedExpGraphs = useAppSelector(state => selectChartsByExperimentId(state, experiment_id))
    const isSocketConnected = useAppSelector(isConnected);

    useEffect(() => {
        console.count(`filteredExp: ${filteredExp}`);
        if (filteredExp) {
            setSelectedExperiment(filteredExp);
        }
    },[filteredExp]);

    return(
        <div className={styles.main}>
            {
                filteredExp && isSocketConnected ?
                <>
                    <Accordion defaultExpanded={true}>
                        <AccordionSummary>
                            <div className={styles.accordian_heading}>Details</div>
                        </AccordionSummary>
                        <AccordionDetails className={styles.accordian_details}>
                            <ExperimentDetails selectedExperiment={selectedExperiment}/>
                        </AccordionDetails>
                    </Accordion>
                    <Accordion defaultExpanded={true}>
                        <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
                            <div className={styles.accordian_heading}>Progress</div>
                        </AccordionSummary>
                        <AccordionDetails>
                            <ExperimentProgress selectedExperiment={selectedExperiment}/>
                        </AccordionDetails>
                    </Accordion>
                    <Accordion defaultExpanded={true}>
                        <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
                            <div className={styles.accordian_heading}>
                                Model Cards
                                <Button 
                                    variant="contained" 
                                    endIcon={<AnalyticsIcon />} 
                                    className={styles.accordian_heading_moedl_card_btn}
                                    onClick={()=>{
                                        navigate({
                                            pathname: '/'+RoutesMapping["ModelCard"].url,
                                            search: '?experiment_id=' + experiment_id,
                                        })
                                    }}
                                >
                                    Full Model Card
                                </Button>
                            </div>
                        </AccordionSummary>
                        <AccordionDetails>
                            <EnvironmentDetails fromPage="ExperimentPage" experiment_id={experiment_id.toString()}/>
                        </AccordionDetails>
                    </Accordion>
                    {
                        filteredExp && filteredExp.hasOwnProperty("experiment_id") ?
                        <Accordion defaultExpanded={true}>
                            <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
                                <div className={styles.accordian_heading}>Configurations</div>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
                                    <Grid item={true} xs={12} sm={12} md={3}>
                                        <CheckpointConfigurations experimentIdProp={filteredExp!.experiment_id.toString()}/>
                                    </Grid>
                                    <Grid item={true} xs={12} sm={12} md={9}>
                                        <ExperimentConfigurations experimentIdProp={filteredExp!.experiment_id.toString()}/>
                                    </Grid>
                                </Grid>
                            </AccordionDetails>
                        </Accordion>
                        :
                        null
                    }
                    <Accordion defaultExpanded={true}>
                        <AccordionSummary>
                            <div className={styles.accordian_heading}>Losses & Metrics</div>
                        </AccordionSummary>
                        <AccordionDetails>
                            {
                                Object.keys(selectedExpGraphs).length > 0 ?
                                <Grid container rowSpacing={1} spacing={{ xs: 2, md: 3 }} className={styles_graphs.grid_container}>
                                    {
                                        Object.keys(selectedExpGraphs).map((chart_id) => 
                                            <Graph 
                                                key={chart_id.toString()} 
                                                chart_id={chart_id.toString()} 
                                                exp_id={selectedExpGraphs[chart_id].exp_id.toString()}
                                                exp_data={selectedExpGraphs[chart_id].data}
                                            />
                                        )
                                    }
                                </Grid>
                                :
                                <Box className={styles_graphs.no_data_to_viz}>
                                    --- No Data To Visualize ---
                                </Box>
                            }
                        </AccordionDetails>
                    </Accordion>
                </>
                :
                isSocketConnected ?
                <div className={styles.extra_text_container}>
                    <div className={styles.error_text_no_data_1}> No Data Available </div>
                    <div className={styles.error_text_no_data_2}> (Please wait, experiment details might be loading...) </div>
                </div>
                :
                null
            }
        </div>
    )
}

export default ExperimentPage;