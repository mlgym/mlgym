import { Box, Card, Grid } from "@mui/material";
import { ChartOptions } from "chart.js";
import { Line } from "react-chartjs-2";
import { useAppSelector } from "../../app/hooks";
import { selectChartLabelsById, selectExperimentsPerChartById } from "../../redux/charts/chartsSlice";
import { selectColorMap } from "../../redux/status/statusSlice";
// styles
import styles from "./Graphs.module.css";

// https://www.chartjs.org/docs/latest/general/data-structures.html

// export default function Graph(data: any, options: any, index: number) {
export default function Graph({ chart_id }: { chart_id: string }) {

    const chartLabels = useAppSelector(state => selectChartLabelsById(state, chart_id));
    const experimentsDic = useAppSelector(state => selectExperimentsPerChartById(state, chart_id));
    const colors = useAppSelector(selectColorMap);

    // prepare data (Warning Looping!)
    const data = {
        labels: chartLabels, // the X-axis:Array<number>
        datasets: !experimentsDic ? [] :
            // loop over the experiments in the ChartF
            Object.values(experimentsDic).map(exp => ({
                label: "experiment_" + exp!.exp_id, // exp_name
                data: exp!.data, // exp_values:Array<number>, Y-axis, same size as X-axis
                fill: false,
                backgroundColor: colors[exp!.exp_id],
                borderColor: colors[exp!.exp_id],
                tension: 0, // to give smoothness to the line curves
            })),
    };

    // NOTE: casting as ChartOptions happens later, otherwise the radius parameters will give errors!!!
    const options = {
        plugins: {
            title: {
                text: chart_id,
                display: true,
                color: 'black',
                font: {
                    weight: 'bold',
                    size: 20 //'20px'
                }
            },
            legend: {
                display: true,
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            }
        },
        animation: {
            duration: 300,
            easing: 'linear'
        },
        radius: 3,  // radius of the label tag
        hoverRadius: 12, // on hover:: change of data point radius size
        hitRadius: 20, // radius of mouse to show the label values when mouse is near a datapoint
        responsive: true,
        maintainAspectRatio: false,
    };

    return (
        <Grid item={true} xs={12} sm={12} md={6} key={chart_id}>
            <Card className={styles.grid_card}>
                <Box className={styles.graphs_chart_container}>
                    <Line
                        data={data}
                        options={options as ChartOptions}
                    />
                </Box>
            </Card>
        </Grid>
    );
}