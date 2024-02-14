import { CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js';
import { useAppSelector } from "../../app/hooks";
import { selectChartIds, selectChartsCount } from "../../redux/charts/chartsSlice";
import Graph from './Graph';
// mui components & styles
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import styles from "./Graphs.module.css";
//NOTE: react-chartjs-2 is a wrapper around vanila javascript chart.js and this is why registering is needed!
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


export default function Graphs() {
    const chartIds = useAppSelector(selectChartIds);
    const chartsCount = useAppSelector(selectChartsCount);

    return (
        <Box component="main" className={styles.graphs_main_container}>
            {
                chartsCount > 0 ?
                    <Grid container rowSpacing={1} spacing={{ xs: 2, md: 3 }} className={styles.grid_container}>
                        {
                            chartIds.map(chart_id => <Graph chart_id={chart_id.toString()} key={chart_id.toString()} />)
                        }
                    </Grid>
                    :
                    <Box className={styles.no_data_to_viz}>
                        --- No Data To Visualize ---
                    </Box>
            }
        </Box>
    );
}