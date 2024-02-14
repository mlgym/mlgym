import { Grid } from '@mui/material';
import { useEffect, useState } from 'react';
import HyperParameterListAndDetails from './HyperParameterListAndDetails';
import TrainingDataExceptHyperparams from './TrainingDataExceptHyperparams';
import { AnyKeyValuePairs } from '../../../app/interfaces';


export default function TrainingDetails({trainingDetails} : {trainingDetails: AnyKeyValuePairs}) {

    const [filteredTrainingData, setFilteredTrainingData] = useState<AnyKeyValuePairs>({});

    useEffect(()=>{
        const filteredTrainingData = { ...trainingDetails };
        delete filteredTrainingData["hyperparams"];
        setFilteredTrainingData(filteredTrainingData);
    },[trainingDetails])

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