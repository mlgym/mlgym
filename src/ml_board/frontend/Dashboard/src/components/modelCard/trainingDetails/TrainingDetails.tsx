import { Grid } from '@mui/material';
import { useEffect, useState } from 'react';
import { AnyKeyValuePairsInterface } from '../../experimentPage/ExperimentPage';
import HyperParameterListAndDetails from './HyperParameterListAndDetails';
import TrainingDataExceptHyperparams from './TrainingDataExceptHyperparams';

var anyObj: AnyKeyValuePairsInterface = {}

export default function TrainingDetails({trainingDetails} : {trainingDetails: AnyKeyValuePairsInterface}) {

    const [filteredTrainingData, setFilteredTrainingData] = useState(anyObj);

    useEffect(()=>{
        const filteredTrainingData = { ...trainingDetails };
        delete filteredTrainingData["hyperparams"];
        setFilteredTrainingData(filteredTrainingData);
    },[])

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <TrainingDataExceptHyperparams 
                    filteredTrainingData={filteredTrainingData}
                />
            </Grid>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <HyperParameterListAndDetails 
                    hyperparams={trainingDetails.hyperparams}
                />
            </Grid>
        </Grid>
    );
}