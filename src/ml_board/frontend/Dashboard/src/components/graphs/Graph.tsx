import { ChartData, ChartOptions } from "chart.js";
import { useMemo } from 'react';
import { Line } from "react-chartjs-2";
import { RoutesMapping } from "../../app/RoutesMapping";
import { useAppSelector } from "../../app/hooks";
import { selectChartLabelsById, selectExperimentsPerChartById } from "../../redux/charts/chartsSlice";
import { selectTab } from "../../redux/globalConfig/globalConfigSlice";
import SelectExperimentDropdown from "./SelectExperimentDropdown/SelectExperimentDropdown";
// styles
import { Box, Card, Grid } from "@mui/material";
import styles from "./Graphs.module.css";

const selectColor = (index: number): string => `hsl(${index * 137.5},75%,50%)`;
// `#${Math.floor(Math.random() * 16777215).toString(16)}`; // totally random and so one can only hope that it doesn't produce a blue blue blue blue blue... pattern :')

// https://www.chartjs.org/docs/latest/general/data-structures.html

export default function Graph({ chart_id, exp_id, exp_data }: { chart_id: string, exp_id?:string, exp_data?: Array<number> }) {

    const chartLabels = useAppSelector(state => selectChartLabelsById(state, chart_id));
    const experimentsDict = useAppSelector(state => selectExperimentsPerChartById(state, chart_id));
    const tab = useAppSelector(selectTab);

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
        const index = legendItem.datasetIndex;
        const ci = legend.chart;
        const meta = ci.getDatasetMeta(index);

        // Get the indexes of datasets with hidden === false
        const visibleIndexes = ci.data.datasets.reduce(function(acc:any, dataset:any, i:any) {
            let otherMeta = ci.getDatasetMeta(i);
            if (otherMeta.hidden === false) {
                acc.push(i);
            }
            return acc;
        }, []);

        // Toggle visibility of clicked dataset
        if(meta.hidden === false) {
            // if the experiment was already selected to be shown and so others were hidden.
            // so, when only one experiment is been shown and when you click on it again, show all the experiments (i.e unhide all the other experiments)
            // I suggest that you try playing with hiding and unhiding the experiments on the frontend - you will get a clear idea! :-)
            if(visibleIndexes.length === 1) {
                ci.data.datasets.forEach(function(dataset:any, i:any) {
                    let otherMeta = ci.getDatasetMeta(i);
                    otherMeta.hidden = null;
                });
            }
            else {
                // when multiple experiments are selected and been shown, at that time
                // if this experiment was also been shown and if you click on it again, this will hide it 
                meta.hidden = true;
            }
        }
        else {
            // unhide/show the selected experiment and hide the rest of them (that's why forEach loop)
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

    // using Memo didn't solve the problem of the selectExperimentsPerChartById selector inside SelectExperimentDropdown
    // const selectExpDropDown = useMemo(() => <SelectExperimentDropdown chart_id={chart_id} />, [chart_id]);
    
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
                    tab === RoutesMapping["ExperimentPage"].url || tab === RoutesMapping["ModelCard"].url ?
                    null
                    :
                    <SelectExperimentDropdown chart_id={chart_id} />

                }
            </Card>
        </Grid>
    );
}