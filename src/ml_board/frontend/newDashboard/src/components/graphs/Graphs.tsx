import { useSelector } from 'react-redux';
import { Line } from "react-chartjs-2";
import './Graphs.css';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
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
    const evalResult = useSelector((state:any) => state.experimentsSlice.evalResult);

    return(
        <div>
            <div className="home-main-h2">
                Training Scores & Loss
            </div>
            {
                Object.keys(evalResult.experiments).length > 0 ?
                <div className="home-main">
                    {
                        Object.keys(evalResult.experiments).map((loss_or_metric, index) => {
                            return(
                                <div className="home-child" key={index}>
                                    <Line 
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