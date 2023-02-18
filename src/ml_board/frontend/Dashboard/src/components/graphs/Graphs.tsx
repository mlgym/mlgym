import { Line } from "react-chartjs-2";
import { useSelector } from 'react-redux';
// import { reduxState } from "../../redux/store";
import { CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Grid from '@mui/material/Grid';
import graphs_css from "./GraphsCss";
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

function Graphs () {
    // TODO Vijul: alway useAppSelector never useSelector
    const evalResult = useSelector((state: any) => state.experimentsSlice.evalResult);

    // TODO: const chartIds = useAppSelector(selectChartIds);
    // TODO: const charts = useAppSelector(selectCharts);
    // TODO: const chartsCount = useAppSelector(selectChartsCount);
     
    return(
        <Box component="main" sx={graphs_css.graphs_main_container}>
            <Toolbar />
            {
                // TODO: chartsCount > 0 ?
                Object.keys(evalResult.experiments).length > 0 ?
                <Grid container rowSpacing={1} spacing={{ xs: 2, md: 3 }} sx={graphs_css.grid_container}>
                    {
                        // TODO: chartIds.map((loss_or_metric, index) => {
                        Object.keys(evalResult.experiments).map((loss_or_metric, index) => {
                            return(
                                <Grid item={true} xs={12} sm={12} md={6} key={index}>
                                    <Card sx={graphs_css.grid_card}>
                                        <Box sx={graphs_css.graphs_chart_container}>
                                            <Line
                                                // TODO: data={charts[loss_or_metric].data} 
                                                // TODO: options={charts[loss_or_metric].options}
                                                data={evalResult.experiments[loss_or_metric].data} 
                                                options={evalResult.experiments[loss_or_metric].options}
                                            />
                                        </Box>
                                    </Card>
                                </Grid>
                            )
                        })
                    }
                </Grid>
                :
                <Box sx={graphs_css.no_data_to_viz}>
                    --- No Data To Visualize ---
                </Box>
            } 
        </Box>
    );
}

export default Graphs;