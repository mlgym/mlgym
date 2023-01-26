import React from "react";
import { connect, useSelector } from 'react-redux';
import { Line } from "react-chartjs-2";
import './Home.css';
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

function Home () {
    const evalResult = useSelector((state:any) => state.ExperimentsReducer.evalResult);

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

const mapStateToProps = (state: any) => ({
    evalResult: state.ExperimentsReducer.evalResult
});

export default connect(mapStateToProps)(Home);