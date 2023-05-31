import { Grid, Card, CardContent } from '@mui/material';
import { useEffect, useState } from 'react';
import axios from 'axios';
import api from '../../../app/ApiMaster';
import { useAppSelector } from "../../../app/hooks";
import { getGridSearchId, getRestApiUrl } from '../../../redux/globalConfig/globalConfigSlice';
import styles from './ModelCards.module.css';
import { AnyKeyValuePairsInterface } from '../ExperimentPage';
import { CardDetails } from '../ExperimentDetails/CardDetails';
import ModelCardCudaList from './ModelCardCudaList';
import ModelCardPythonPackagesList from './ModelCardPythonPackagesList';

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

export default function ModelCards({experimentIdProp} : {experimentIdProp: string}) {

    const grid_search_id = useAppSelector(getGridSearchId);
    const rest_api_url = useAppSelector(getRestApiUrl);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const[sysInfoBasicData, setSysInfoBasicData] = useState(sysInfoAnyKeyObj);
    const[sysInfoCudaDevicesData, setSysInfoCudaDevicesData] = useState(Array<cudaDeviceListInterface>);
    const[sysInfoPythonPackages, setSysInfoPythonPackages] = useState([]);


    useEffect(() => {
        if(experimentIdProp) {
            getSysInfo();
        }
    },[experimentIdProp]);

    function getSysInfo() {
        let model_card_sys_info = api.model_card_sys_info.replace("<grid_search_id>", grid_search_id);
        model_card_sys_info = model_card_sys_info.replace("<experiment_id>", experimentIdProp);

        setError("");
        setIsLoading(true);

        axios.get(rest_api_url + model_card_sys_info).then((response) => {
            console.log("Got response from model_card_sys_info API: ", response);
            if (response.status === 200) {
                let resp_data = response.data;
                Object.keys(resp_data).map((sysInfoKeyName) => {
                    if(sysInfoKeyName === "cuda_device_list") {
                        setSysInfoCudaDevicesData(resp_data[sysInfoKeyName]);
                    }
                    else if(sysInfoKeyName === "python-packages") {
                        setSysInfoPythonPackages(resp_data[sysInfoKeyName])
                    }
                    else {
                        sysInfoBasicData[sysInfoKeyName] = resp_data[sysInfoKeyName];
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
                        <ModelCardCudaList 
                            cardTitle="Cuda Devices List" 
                            cudaDeviceList={sysInfoCudaDevicesData}
                        />
                    </Grid>
                    <Grid item={true} xs={12} sm={12} md={4}>
                        <ModelCardPythonPackagesList 
                            cardTitle="Python Packages List" 
                            pythonPackagesList={sysInfoPythonPackages}
                        />
                    </Grid>
                </Grid>
            }
            </Grid>
        </Grid>
    );
}