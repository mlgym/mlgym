import React from "react";
import { connect, useSelector } from 'react-redux';
import { Line } from "react-chartjs-2";
import CSS from 'csstype';
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
            <div style={main_h2}>
                Training Scores & Loss
            </div>
            {
                Object.keys(evalResult.experiments).length > 0 ?
                <div style={main}>
                    {
                        Object.keys(evalResult.experiments).map((loss_or_metric, index) => {
                            return(
                                <div style={child} key={index}>
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

const main_h2: CSS.Properties = {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'lightblue',
        color: 'darkblue',
        fontSize: '30px',
        fontWeight: 'bold',
        padding: '10px',
        marginBottom: '10px'
}

const main: CSS.Properties = {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    flexWrap: 'wrap'
}

const child: CSS.Properties = {
    width: "40%",
    height: "70%",
    marginLeft: "20px",
    marginRight: "20px"
}

const mapStateToProps = (state: any) => ({
    evalResult: state.ExperimentsReducer.evalResult
});

export default connect(mapStateToProps)(Home);