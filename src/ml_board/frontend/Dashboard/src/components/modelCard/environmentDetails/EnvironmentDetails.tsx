import { Grid, Card, CardContent } from '@mui/material';
import { useEffect, useState } from 'react';
import mock_data from "./dummy_data.json";
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
    },[fromPage, experiment_id, tableRows, sysInfoBasicDataProps, sysInfoCudaDevicesDataProps, sysInfoPythonPackagesProps, sysInfoArchitectureProps, sysInfoCarbonFootPrintDetailsProps, sysInfoEntryPointCmdDetailsProps]);

    function getSysInfo() {
        // const model_card_sys_info = api.model_card_sys_info
        //                                 .replace("<grid_search_id>", grid_search_id)
        //                                 .replace("<experiment_id>", experiment_id);
        const {
            model_details, training_details, eval_details, pipeline_details,
            experiment_environment: { carbon_footprint, entry_point_cmd,
                system_env: { cuda_device_list, architecture,
                    "python-packages": python_packages, ...sysInfoBasicData }
            }
        } = mock_data as AnyKeyValuePairs;
        setSysInfoCarbonFootPrintDetails(carbon_footprint);
        setSysInfoEntryPointCmdDetails(entry_point_cmd);
        setSysInfoCudaDevicesData(cuda_device_list);
        setSysInfoPythonPackages(python_packages);
        setSysInfoArchitecture(architecture);
        setSysInfoBasicData(sysInfoBasicData);
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