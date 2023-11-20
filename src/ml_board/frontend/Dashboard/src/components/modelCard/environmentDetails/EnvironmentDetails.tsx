import { Grid, Card, CardContent } from '@mui/material';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api from '../../../app/ApiMaster';
import { useAppSelector } from "../../../app/hooks";
import { getGridSearchId, getRestApiUrl, isConnected } from '../../../redux/globalConfig/globalConfigSlice';
import styles from './EnvironmentDetails.module.css';
import { CardDetails } from '../../experimentPage/ExperimentDetails/CardDetails';
import CudaList from './CudaList';
import PythonPackagesList from './PythonPackagesList';
import { AnyKeyValuePairs } from '../../../app/interfaces';

export interface pythonPackagesListInterface {
    "name": string,
    "version": string
}

export interface cudaDeviceListInterface {
    "name": string,
    "multi_proc_count": string,
    "total_memory": string
}

interface EnvironmentDetailsProps {
    fromPage: string,
    experiment_id: string,
    tableRows?: number, sysInfoBasicDataProps?: AnyKeyValuePairs,
    sysInfoCudaDevicesDataProps?: Array<cudaDeviceListInterface>,
    sysInfoPythonPackagesProps?: Array<pythonPackagesListInterface>,
    sysInfoArchitectureProps?: Array<"">, sysInfoCarbonFootPrintDetailsProps?: string,
    sysInfoEntryPointCmdDetailsProps?: string
}

export default function EnvironmentDetails({fromPage, experiment_id, tableRows, sysInfoBasicDataProps, sysInfoCudaDevicesDataProps, sysInfoPythonPackagesProps, sysInfoArchitectureProps, sysInfoCarbonFootPrintDetailsProps, sysInfoEntryPointCmdDetailsProps} : EnvironmentDetailsProps) {

    const isSocketConnected = useAppSelector(isConnected);
    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const[sysInfoBasicData, setSysInfoBasicData] = useState<AnyKeyValuePairs>({});
    const[sysInfoCudaDevicesData, setSysInfoCudaDevicesData] = useState(Array<cudaDeviceListInterface>);
    const [sysInfoPythonPackages, setSysInfoPythonPackages] = useState(Array<pythonPackagesListInterface>);
    const [sysInfoArchitecture, setSysInfoArchitecture] = useState(Array<"">);
    const [sysInfoCarbonFootPrintDetails,setSysInfoCarbonFootPrintDetails] = useState("");
    const [sysInfoEntryPointCmdDetails,setSysInfoEntryPointCmdDetails] = useState("");

    useEffect(() => {
        if(fromPage === "ModelCard") {
            setSysInfoBasicData(sysInfoBasicDataProps!);
            setSysInfoCudaDevicesData(sysInfoCudaDevicesDataProps!);
            setSysInfoPythonPackages(sysInfoPythonPackagesProps!);
            setSysInfoArchitecture(sysInfoArchitectureProps!);
            setSysInfoCarbonFootPrintDetails(sysInfoCarbonFootPrintDetailsProps!);
            setSysInfoEntryPointCmdDetails(sysInfoEntryPointCmdDetailsProps!);
        }
        else {
            getSysInfo();
        }
    },[]);

    function getSysInfo() {
        let model_card_sys_info = api.model_card_sys_info.replace("<grid_search_id>", grid_search_id);
        model_card_sys_info = model_card_sys_info.replace("<experiment_id>", experiment_id);

        setError("");
        setIsLoading(true);

        axios.get("http://" + rest_api_url + model_card_sys_info).then((response) => {
            console.log("Got response from model_card_sys_info API: ", response);
            if (response.status === 200) {
                let resp_data = response.data;
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

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
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
                <Grid container rowSpacing={1} spacing={{ xs: 1, md: 2 }}>
                    <Grid item={true} xs={12} sm={12} md={4}>
                        <CardDetails
                            cardTitle="System Info"
                            contentObj={sysInfoBasicData}
                        />
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={4}>
                        <CudaList 
                            cardTitle="Cuda Devices List" 
                            cudaDeviceList={sysInfoCudaDevicesData}
                            tableRows={
                                tableRows && tableRows !== 0?
                                tableRows
                                :
                                undefined
                            }
                        />
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={4}>
                        <PythonPackagesList 
                            cardTitle="Python Packages List" 
                            pythonPackagesList={sysInfoPythonPackages}
                            tableRows={
                                tableRows && tableRows !== 0?
                                tableRows
                                :
                                undefined
                            }
                        />
                    </Grid>
                </Grid>
            }
            </Grid>
        </Grid>
    );
}