import { Line } from 'react-chartjs-2';
import { CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js';
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
interface LineGraphDataProps {
    graph_data: Array<{
        exp_id: number,
        label: string,
        data: Array<number>,
        fill: Boolean,
        backgroundColor: string,
        borderColor: string,
        tension: number // to give smoothness to the line curves
    }>;
    title_text: string;
}

const LineGraph: React.FC<LineGraphDataProps> = (props) => {
    
    return (
        <Line
            data={{
                labels: Array.from(Array(props.graph_data).keys()),
                datasets: props.graph_data,
            }}
            options={{
                animation: {
                    duration: 0,
                    easing: 'linear'
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: props.title_text.toLowerCase(),
                        color: 'black',
                        font: {
                            weight: 'bold',
                            size: 20
                        }
                    },
                    legend: {
                        display: true,
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                }
            }}
        />
    );
}

export default LineGraph;