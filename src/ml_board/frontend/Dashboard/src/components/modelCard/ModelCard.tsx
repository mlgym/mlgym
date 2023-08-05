import { Box, Button, Card, CardContent, Fab, Grid } from "@mui/material";
import { useSearchParams } from "react-router-dom";
import DatasetDetails from "./datasetDetails/DatasetDetails";
import TrainingDetails from "./trainingDetails/TrainingDetails";
import EvaluationDetails from "./evaluationDetails/EvaluationDetails";
import EnvironmentDetails from "./environmentDetails/EnvironmentDetails";
import styles_graphs from "../graphs/Graphs.module.css";
import Graph from "../graphs/Graph";
import { useAppSelector } from "../../app/hooks";
import { selectChartsByExperimentId } from "../../redux/charts/chartsSlice";
import { CardDetails } from "../experimentPage/ExperimentDetails/CardDetails";
import WorkspacesIcon from '@mui/icons-material/Workspaces';
import StorageIcon from '@mui/icons-material/Storage';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
// import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import InsightsIcon from '@mui/icons-material/Insights';
import ModelTrainingIcon from '@mui/icons-material/ModelTraining';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import styles from './ModelCard.module.css';
// import { jsPDF } from "jspdf";
// import { toPng } from 'html-to-image';
import { useEffect, useState } from "react";
import { getGridSearchId, getRestApiUrl, isConnected } from '../../redux/globalConfig/globalConfigSlice';
import html2canvas from 'html2canvas';
import axios from 'axios';
import api from '../../app/ApiMaster';
import { AnyKeyValuePairsInterface } from '../experimentPage/ExperimentPage';
import DownloadIcon from '@mui/icons-material/Download';

export interface pythonPackagesListInterface {
    "name": string,
    "version": string
}

export interface cudaDeviceListInterface {
    "name": string,
    "multi_proc_count": string,
    "total_memory": string
}
let sysInfoAnyKeyObj:AnyKeyValuePairsInterface = {};

export default function ModelCard() {
    
    const isSocketConnected = useAppSelector(isConnected);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);    
    
    const [searchParams, setSearchParams] = useSearchParams();
    const [tableRows, setTableRows] = useState(0);
    let experiment_id = searchParams.get("experiment_id") as string;
    const selectedExpGraphs = useAppSelector(state => selectChartsByExperimentId(state, experiment_id));
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const [datasetDetails, setDatasetDetails] = useState(sysInfoAnyKeyObj);
    const [evalDetails, setEvalDetails] = useState(sysInfoAnyKeyObj);
    const [modelDetails, setModelDetails] = useState(sysInfoAnyKeyObj);
    const [trainingDetails, setTrainingDetails] = useState(sysInfoAnyKeyObj);

    const [sysInfoBasicData, setSysInfoBasicData] = useState(sysInfoAnyKeyObj);
    const [sysInfoCudaDevicesData, setSysInfoCudaDevicesData] = useState(Array<cudaDeviceListInterface>);
    const [sysInfoPythonPackages, setSysInfoPythonPackages] = useState(Array<pythonPackagesListInterface>);
    const [sysInfoArchitecture, setSysInfoArchitecture] = useState(Array<"">);
    const [sysInfoCarbonFootPrintDetails,setSysInfoCarbonFootPrintDetails] = useState("");
    const [sysInfoEntryPointCmdDetails,setSysInfoEntryPointCmdDetails] = useState("");

    useEffect(() => {
        if(experiment_id && isSocketConnected) {
            getModelCardData();
        }
    },[experiment_id, isSocketConnected]);

    function getModelCardData() {
        let model_card_sys_info = api.model_card_sys_info.replace("<grid_search_id>", grid_search_id);
        model_card_sys_info = model_card_sys_info.replace("<experiment_id>", experiment_id);

        setError("");
        setIsLoading(true);

        axios.get(rest_api_url + model_card_sys_info).then((response) => {
            console.log("Got response from model_card_sys_info API: ", response);
            if (response.status === 200) {
                let resp_data = response.data;
                setModelDetails(resp_data.model_details);
                setTrainingDetails(resp_data.training_details);
                setEvalDetails(resp_data.eval_details);
                setDatasetDetails(resp_data.dataset_details);
                setSysInfoCarbonFootPrintDetails(resp_data.experiment_environment.carbon_footprint);
                setSysInfoEntryPointCmdDetails(resp_data.experiment_environment.entry_point_cmd);
                Object.keys(resp_data.experiment_environment.system_env).map((sysInfoKeyName) => {
                    let data = resp_data.experiment_environment.system_env[sysInfoKeyName];
                    if(sysInfoKeyName === "cuda_device_list") {
                        setSysInfoCudaDevicesData(data);
                    }
                    else if(sysInfoKeyName === "python-packages") {
                        setSysInfoPythonPackages(data)
                    }
                    else if (sysInfoKeyName === "architecture") {
                        setSysInfoArchitecture(data)
                    }
                    else {
                        sysInfoBasicData[sysInfoKeyName] = data;
                    }
                });
                setSysInfoBasicData(sysInfoBasicData);
            }
            else {
                setError("Error occured / No system info available");
            }
            setIsLoading(false);
        })
        .catch((error) => {
            console.log("Error in model_card_sys_info: ", error);
            setIsLoading(false);
            setError("Error occured / No system info available");
        });
    }

    // const downloadPdfDocument = (element_id: string) => {
    //     setTableRows(-1);
    //     // TODO: show loading spinner till this part is processed
    //     setTimeout(() => {
    //         const divElement = document.getElementById(element_id);
    //         const options = {
    //             height: divElement!.offsetHeight, // Adjust the scale factor as needed
    //             style: { transform: 'scale(1)', transformOrigin: 'top left' },
    //         };
    //         toPng(divElement!, options)
    //         .then((dataUrl) => {
    //             // TODO: getting extra pages in pdf. Adjust height of the content so that we don't get extra pages in the pdf
    //             const pdf = new jsPDF('p', 'pt', 'a4');
    //             const pdfWidth = pdf.internal.pageSize.getWidth();
    //             const pdfHeight = pdf.internal.pageSize.getHeight();
        
    //             const imgWidth = pdfWidth;
    //             const imgHeight = (divElement!.offsetHeight / divElement!.offsetWidth) * imgWidth;
        
    //             let position = 0;
    //             const pageData = dataUrl;
        
    //             pdf.addImage(pageData, 'PNG', 0, position, imgWidth, imgHeight);
    //             position -= pdfHeight;
        
    //             while (position > -divElement!.offsetHeight) {
    //                 pdf.addPage();
    //                 pdf.addImage(pageData, 'PNG', 0, position, imgWidth, imgHeight);
    //                 position -= pdfHeight;
    //             }
        
    //             pdf.save(`Experiment_${experiment_id}_ModelCard.pdf`);
    //             setTableRows(0);
    //         })
    //         .catch((error) => {
    //             console.error('Error saving PDF:', error);
    //             setTableRows(0);
    //             // TODO: Show error snackbar
    //         });
    //     }, 200);
    // }

    const handleSaveAsHTML = async () => {
        setTableRows(-1);
        const model_dataset_details = document.getElementById('model_dataset_details') as HTMLElement;
        const training_evaluation = document.getElementById('training_evaluation') as HTMLElement;
        const environment = document.getElementById('environment') as HTMLElement;

        const img = await convertDivToPNG('results_visualization');

        // Collect the CSS styles from style elements and chart stylesheets
        const css_styles = Array.from(document.styleSheets)
        .map((styleSheet) => {
            if (styleSheet.cssRules) {
                return Array.from(styleSheet.cssRules)
                    .map((rule) => rule.cssText)
                    .join('\n');
            }
            return '';
        })
        .join('\n');

        const mainStyles = `
            background-color: #fff;
            padding: 20px;
        `;

        const imgStyles = `
            display: block;
            width: 100%;
            height: 100%;
            object-fit: cover;
        `;

        const card_feel = `
            box-shadow: 0px 0px 3px 2px rgb(0, 0, 0, 0.2);
            border-radius: 5px;
            margin-bottom: 20px;
        `;

        const htmlContent = `
            <!DOCTYPE html>
            <html>
                <head>
                    <title>${`Experiment_${experiment_id}_ModelCard`}</title>
                    <style>
                        ${css_styles}
                    </style>
                </head>
                <body>
                    <div style="${mainStyles}">
                        ${model_dataset_details.outerHTML}
                        ${training_evaluation.outerHTML}
                        <div style="${card_feel}">
                            <img src="${img}" alt="Results Visualizations" style="${imgStyles}"/>
                        </div>
                        ${environment.outerHTML}
                    </div>
                </body>
            </html>
        `;

        setTableRows(0);

        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Experiment_${experiment_id}_ModelCard`;
        link.click();
    }

    const convertDivToPNG = async (divId: string) => {
        const divToCapture = document.getElementById(divId) as HTMLElement;

        try {
            const canvas = await html2canvas(divToCapture, {
                scale: 2, // Increase the scale for higher resolution
                useCORS: true, // Enable CORS to capture images from external domains
            });
            const image = canvas.toDataURL('image/png');
            return image;
        } catch (error) {
            console.error('Error converting div to PNG:', error);
            throw error;
        }
    }
    
    return(
        <div>
            {
                isSocketConnected ?
                <div>
                    {
                        isLoading ?
                        <Card className={styles.cardcontent_model_cards}>
                            <CardContent>
                                <div className={styles.loading_text}> 
                                    Please wait, loading model cards...
                                </div>
                            </CardContent>
                        </Card>
                        :
                        error.length > 0 ?
                        <Card className={styles.cardcontent_model_cards}>
                            <CardContent>
                                <div className={styles.error_text}> 
                                    {error}
                                </div>
                            </CardContent>
                        </Card>
                        :
                        <>  
                            <div className={styles.fab}>
                                <Fab color="primary" onClick={()=>handleSaveAsHTML()}>
                                    <DownloadIcon />
                                </Fab>
                            </div>
                            
                            <div id="modelcard" className={styles.main}>
                                <Grid id="model_dataset_details" container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
                                    
                                    <Grid item={true} xs={12} sm={12} md={6} lg={6}>
                                        <div className={styles.card_feel}>
                                            <div className={styles.title_container}>
                                                <div className={styles.title_container_icon}>
                                                    <WorkspacesIcon/>
                                                </div>
                                                <div className={styles.title_container_text}>
                                                    Model Details
                                                </div>
                                            </div>
                                            <div>
                                                <CardDetails
                                                    cardTitle=""
                                                    contentObj={modelDetails}
                                                />
                                            </div>
                                        </div>
                                    </Grid>

                                    <Grid item={true} xs={12} sm={12} md={6} lg={6}>
                                        <div className={styles.card_feel}>
                                            <div className={styles.title_container}>
                                                <div className={styles.title_container_icon}>
                                                    <StorageIcon/>
                                                </div>
                                                <div className={styles.title_container_text}>
                                                    Dataset Details
                                                </div>
                                            </div>
                                            <div>
                                                <DatasetDetails
                                                    datasetDetails={datasetDetails}
                                                />
                                            </div>
                                        </div>
                                    </Grid>

                                </Grid>

                                <Grid 
                                    id="training_evaluation"
                                    container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}
                                    className={styles.grid_contianer}
                                >
                                    <Grid item={true} xs={12} sm={12} md={6} lg={6}>
                                        <div className={styles.card_feel}>
                                            <div className={styles.title_container}>
                                                <div className={styles.title_container_icon}>
                                                    <ModelTrainingIcon />
                                                </div>
                                                <div className={styles.title_container_text}>
                                                    Training
                                                </div>
                                            </div>
                                            <div>
                                                <TrainingDetails
                                                    trainingDetails={trainingDetails}
                                                />
                                            </div>
                                        </div>
                                    </Grid>
                                    <Grid item={true} xs={12} sm={12} md={6} lg={6}>
                                        <div className={styles.card_feel}>
                                            <div className={styles.title_container}>
                                                <div className={styles.title_container_icon}>
                                                    <QueryStatsIcon />
                                                </div>
                                                <div className={styles.title_container_text}>
                                                    Evaluation
                                                </div>
                                            </div>
                                            <div>
                                                <EvaluationDetails
                                                    evalDetails={evalDetails}
                                                />
                                            </div>
                                        </div>
                                    </Grid>
                                </Grid>
                                
                                <div id="results_visualization" className={styles.card_feel}>
                                    <div className={styles.title_container}>
                                        <div className={styles.title_container_icon}>
                                            <InsightsIcon />
                                        </div>
                                        <div className={styles.title_container_text}>
                                            Results Visualizations
                                        </div>
                                    </div>
                                    <div style={{ marginTop: "5px"}}>
                                        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
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
                                        </Grid>
                                    </div>
                                </div>

                                <div id="environment" className={styles.card_feel}>
                                    <div className={styles.title_container}>
                                        <div className={styles.title_container_icon}>
                                            <TravelExploreIcon />
                                        </div>
                                        <div className={styles.title_container_text}>
                                            Environment
                                        </div>
                                    </div>
                                    <div style={{ marginTop: "5px"}}>
                                        <EnvironmentDetails 
                                            fromPage="ModelCard"
                                            experiment_id={experiment_id} 
                                            tableRows={tableRows}
                                            sysInfoBasicDataProps={sysInfoBasicData}
                                            sysInfoCudaDevicesDataProps={sysInfoCudaDevicesData}
                                            sysInfoPythonPackagesProps={sysInfoPythonPackages}
                                            sysInfoArchitectureProps={sysInfoArchitecture}
                                            sysInfoCarbonFootPrintDetailsProps={sysInfoCarbonFootPrintDetails}
                                            sysInfoEntryPointCmdDetailsProps={sysInfoEntryPointCmdDetails}
                                        />
                                    </div>
                                </div>
                            </div>
                        </>
                    }
                </div>
                :
                null
            }
        </div>
    );
}
