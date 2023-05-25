import { Box, Card, Grid } from "@mui/material";
import { ChartData, ChartOptions } from "chart.js";
import { Line } from "react-chartjs-2";
import { useAppSelector } from "../../app/hooks";
import { selectChartLabelsById, selectExperimentsPerChartById } from "../../redux/charts/chartsSlice";
import SelectExperimentDropdown from "./SelectExperimentDropdown/SelectExperimentDropdown";
// styles
import styles from "./Graphs.module.css";
import { RoutesMapping } from "../../app/RoutesMapping";
import { useLocation } from "react-router-dom";

const selectColor = (index: number): string => `hsl(${index * 137.5},75%,50%)`;

// https://www.chartjs.org/docs/latest/general/data-structures.html

export default function Graph({ chart_id, exp_id, exp_data }: { chart_id: string, exp_id?:string, exp_data?: Array<number> }) {

    const chartLabels = useAppSelector(state => selectChartLabelsById(state, chart_id));
    const experimentsDict = useAppSelector(state => selectExperimentsPerChartById(state, chart_id));
    const location = useLocation();
    
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

    const legendOnClickHandler = function (event:any, legendItem:any, legend:any) {
        let index = legendItem.datasetIndex;
        let ci = legend.chart;
        let meta = ci.getDatasetMeta(index);

        // Get the indexes of datasets with hidden === false
        let visibleIndexes = ci.data.datasets.reduce(function(acc:any, dataset:any, i:any) {
            let otherMeta = ci.getDatasetMeta(i);
            if (otherMeta.hidden === false) {
                acc.push(i);
            }
            return acc;
        }, []);

        // Toggle visibility of clicked dataset
        if(meta.hidden === false) {
            if(visibleIndexes.length === 1) {
                ci.data.datasets.forEach(function(dataset:any, i:any) {
                    let otherMeta = ci.getDatasetMeta(i);
                    otherMeta.hidden = null;
                });
            }
            else {
                if(meta.hidden === false) {
                    meta.hidden = true;
                }
            }
        }
        else {
            meta.hidden = false;
            ci.data.datasets.forEach(function(dataset:any, i:any) {
                let otherMeta = ci.getDatasetMeta(i);
                if (otherMeta.hidden === null && i !== index) {
                    otherMeta.hidden = true;
                }
            });
        }

        // Update chart
        ci.update();
    };

    const legendOnHoverHandler = function (event:any, legendItem:any, legend:any) {
        event.chart.canvas.style.cursor = "pointer";
    }

    const legendOnLeaveHandler = function (event:any, legendItem:any, legend:any) {
        event.chart.canvas.style.cursor = "default";
    }

    // NOTE: https://www.chartjs.org/docs/latest/general/performance.html
    const options: ChartOptions<'line'> = {
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
                onClick: legendOnClickHandler,
                onHover: legendOnHoverHandler,
                onLeave: legendOnLeaveHandler,
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                callbacks: {
                    title: (tooltipItems:any) => {
                        return 'Epoch: ' + tooltipItems[0].label;
                    }
                }
            }
        },
        elements: {
            point: {
                radius: 1,  // radius of the label tag
                hitRadius: 10, // radius of mouse to show the label values when mouse is near a datapoint
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Epochs',
                },
            }
        },
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
    }

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
                {
                    location.pathname.split("/")[1] !== RoutesMapping["ExperimentPage"].url ?
                    <SelectExperimentDropdown chart_id={chart_id} />
                    :
                    null
                }
            </Card>
        </Grid>
    );
}