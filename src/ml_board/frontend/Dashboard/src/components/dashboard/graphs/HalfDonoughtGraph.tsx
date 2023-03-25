
import { Doughnut } from 'react-chartjs-2';
import styles from './HalfDonoughtGraph.module.css';
import { Chart as ChartJS, Filler, ArcElement, Tooltip, Legend } from 'chart.js';
ChartJS.register(
    ArcElement,
    Tooltip,
    Legend,
    Filler
);

interface HalfDonoughtGraphDataProps {
    graph_data: Array<Number>;
    progress_text: string;
}

const HalfDonoughtGraph: React.FC<HalfDonoughtGraphDataProps> = (props) => {
    
    return (
        <Doughnut
            className={styles.donought}
            data={{
                // labels: ['Blue'],
                datasets: [
                    {
                        data: props.graph_data,
                        backgroundColor: [
                            "#36A2EB",
                            "transparent"
                        ],
                        borderColor: "#D1D6DC",
                        borderWidth: 1,
                    },
                ],
            }}
            options={{
                animation: {
                    duration: 0,
                    easing: 'linear'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                rotation: -90,
                circumference: 180,
                cutout: "70%",
                maintainAspectRatio: true,
                responsive: true
            }}
            plugins={[{
                id: "textCenter",
                beforeDatasetDraw(chart, args, pluginOptions) {
                    const {ctx, data} = chart;
                    ctx.save();
                    ctx.font = 'bolder 40px sans-serif';
                    ctx.fillStyle = '#36A2EB';
                    ctx.textAlign = 'center';
                    ctx.fillText(props.progress_text, chart.getDatasetMeta(0).data[0].x, chart.getDatasetMeta(0).data[0].y)
                }
            }]}
        />        
    );
}

export default HalfDonoughtGraph;