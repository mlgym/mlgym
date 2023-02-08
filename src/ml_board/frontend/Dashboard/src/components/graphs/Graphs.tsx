import { Line } from "react-chartjs-2";
import { useSelector } from 'react-redux';
// import { reduxState } from "../../redux/store";
import { CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js';
import './Graphs.css';
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
        <div>
            <div className="home-main-h2">
                Training Scores & Loss
            </div>
            {
                // TODO: chartsCount > 0 ?
                Object.keys(evalResult.experiments).length > 0 ?
                <div className="home-main">
                    {
                        // TODO: chartIds.map((loss_or_metric, index) => {
                        Object.keys(evalResult.experiments).map((loss_or_metric, index) => {
                            return(
                                <div className="home-child" key={index}>
                                    <Line 
                                        // TODO: data={charts[loss_or_metric].data} 
                                        // TODO: options={charts[loss_or_metric].options}
                                        data={evalResult.experiments[loss_or_metric].data} 
                                        options={evalResult.experiments[loss_or_metric].options}
                                    />
                                </div>
                            )
                        })
                    }
                </div>
                :
                null
            } 
        </div>
    );
}

export default Graphs;