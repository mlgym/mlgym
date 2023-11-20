import { Grid } from '@mui/material';
import LossFunctionsList from './LossFunctionsList';
import MetricsListAndDetails from './MetricsListAndDetails';
import { AnyKeyValuePairs } from '../../../app/interfaces';

export default function EvaluationDetails({evalDetails} : {evalDetails: AnyKeyValuePairs}) {

    return(
        <Grid container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <LossFunctionsList
                    lossFunctionsList={evalDetails.loss_funcs}
                />
            </Grid>
            <Grid item={true} xs={12} sm={12} md={12} lg={12}>
                <MetricsListAndDetails 
                    metrics={evalDetails.metrics}
                />
            </Grid>
        </Grid>
    );
}
