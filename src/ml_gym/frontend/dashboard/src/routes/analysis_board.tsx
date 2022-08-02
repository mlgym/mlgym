import React from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from "recharts";
import type { RootState } from '../app/store';
import { ModelEvaluationType, ModelEvaluationPayloadType } from "../app/datatypes"
import { useAppSelector } from "../app/hooks"


type AnalysisBoardProps = {
};


const data = [
    {
        name: "Page A",
        uv: 4000,
        pv: 2400,
        amt: 2400
    },
    {
        name: "Page B",
        uv: 3000,
        pv: 1398,
        amt: 2210
    },
    {
        name: "Page C",
        uv: 2000,
        pv: 9800,
        amt: 2290
    },
    {
        name: "Page D",
        uv: 2780,
        pv: 3908,
        amt: 2000
    },
    {
        name: "Page E",
        uv: 1890,
        pv: 4800,
        amt: 2181
    },
    {
        name: "Page F",
        uv: 2390,
        pv: 3800,
        amt: 2500
    },
    {
        name: "Page G",
        uv: 3490,
        pv: 4300,
        amt: 2100
    }
];


export const modelEvaluationSelector = (state: RootState) => state.modelsEvaluation.messages.reduce((results: any, s: ModelEvaluationType) => {
    // results: {metric_key_1: [{name: 0, experiment_id_1: 0.1, ..., experiment_id_n: 0.4}, {name: 1, experiment_id_2: ...}, ...]}

    const modelEvaluationPayload: ModelEvaluationPayloadType = s.data.payload

    const epoch = modelEvaluationPayload.epoch
    const eId = modelEvaluationPayload.experiment_id
    const lossScores = modelEvaluationPayload.loss_scores
    const metricScores = modelEvaluationPayload.metric_scores

    for (const metricScore of metricScores) {
        const fullMetricName = metricScore.split + "/" + metricScore.metric
        if (!results[fullMetricName]) {
            results[fullMetricName] = [{ name: epoch }]
        }
        results[fullMetricName][epoch] = { ...results[fullMetricName][epoch], [eId]: metricScore.score }
    }

    return results
}, {});

export const filteredModelEvaluationSelector = (state: RootState, metricFilter: string) => {
    // results: {experiment_id_1: [0.9, 0.3, ...]}
    const results = modelEvaluationSelector(state)
    if (results[metricFilter]) {
        return results[metricFilter]
    } else {
        return []
    }
};


const AnalysisBoard: React.FC<AnalysisBoardProps> = ({ }) => {

    const metricFilter = ["train/F1_SCORE_macro", "val/F1_SCORE_macro", "test/F1_SCORE_macro"]

    const metricSelector = useAppSelector((state: RootState) => filteredModelEvaluationSelector(state, "test/F1_SCORE_macro"))

    return (
        <>
            <h1> Analysis Board </h1>
            <LineChart
                width={500}
                height={300}
                data={metricSelector}
                margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5
                }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                    type="monotone"
                    dataKey="2022-04-29--22-25-49/conv_net/1"
                    stroke="#8884d8"
                    activeDot={{ r: 8 }}
                />
                {/* <Line type="monotone" dataKey="uv" stroke="#82ca9d" /> */}
            </LineChart>
        </>
    );
}

export default AnalysisBoard;