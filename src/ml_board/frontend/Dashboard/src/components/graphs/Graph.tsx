import { Box, Card, Grid } from "@mui/material";
import { ChartData, ChartOptions } from "chart.js";
import { Line } from "react-chartjs-2";
import { useAppSelector } from "../../app/hooks";
import { selectChartLabelsById, selectExperimentsPerChartById } from "../../redux/charts/chartsSlice";
// styles
import styles from "./Graphs.module.css";

const selectColor = (index: number): string => `hsl(${index * 137.5},75%,50%)`;

// https://www.chartjs.org/docs/latest/general/data-structures.html

export default function Graph({ chart_id, exp_id, exp_data }: { chart_id: string, exp_id?:string, exp_data?: Array<number> }) {

    const chartLabels = useAppSelector(state => selectChartLabelsById(state, chart_id));
    const experimentsDict = useAppSelector(state => selectExperimentsPerChartById(state, chart_id));

    // prepare data (Warning Looping!)
    const data: ChartData<"line"> = {
        // labels = the X-axis:Array<number>
        labels: 
            exp_id && exp_data ?
            Array.from({ length: exp_data.length }, (_, i) => i)
            :
            chartLabels, 
        datasets: 
            exp_id && exp_data ?
            [{
                label: "experiment_" + exp_id, // exp_name
                data: exp_data, // exp_values:Array<number>, Y-axis, same size as X-axis
                backgroundColor: selectColor(Number(exp_id)),
                borderColor: selectColor(Number(exp_id)),
            }]
            :
            !experimentsDict ? 
            [] 
            :
            Object.values(experimentsDict).map(exp => ({
                label: "experiment_" + exp!.exp_id, // exp_name
                data: exp!.data, // exp_values:Array<number>, Y-axis, same size as X-axis
                backgroundColor: selectColor(exp!.exp_id),
                borderColor: selectColor(exp!.exp_id),
            })),
    };

    // NOTE: https://www.chartjs.org/docs/latest/general/performance.html
    const options: ChartOptions = {
        datasets:{
            line:{
                fill: false,
                spanGaps: true,
                normalized: true,
                // TODO: doesn't work! (I tried saving the x_axis values as string not number, no luck either!)
                // parsing: false, 
                pointRadius:0,
                // showLine: false,
                // // Automatic data decimation during draw happens if these 3 values are left as default!
                // tension:0, // 0 for straight lines otherwise curvy lines
                // stepped:false,
                // borderDash:[],
            }
        },
        plugins: {
            title: {
                text: chart_id.toLowerCase().split("_").join(" "),
                display: true,
                color: 'black',
                font: {
                    weight: 'bold',
                    size: 20 //'20px'
                }
            },
            legend: {
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            }
        },
        elements: {
            point: {
                radius: 1,  // radius of the label tag
                hitRadius: 10, // radius of mouse to show the label values when mouse is near a datapoint
            }
        },
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
    };

    return (
        <Grid item={true} xs={12} sm={12} md={6} key={chart_id}>
            <Card className={styles.grid_card}>
                <Box className={styles.graphs_chart_container}>
                    <Line
                        datasetIdKey={chart_id}
                        data={data}
                        options={options}
                    />
                </Box>
            </Card>
        </Grid>
    );
}