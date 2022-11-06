import "./analysis_board.css";

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
import { ModelEvaluationType, ModelEvaluationPayloadType, FilterConfigType } from "../app/datatypes"
import { useAppSelector } from "../app/hooks"


function selectColor(index: number) {
    const hue = index * 137.508; // use golden angle approximation
    return `hsl(${hue},50%,75%)`;
}

type AnalysisBoardProps = {
    filterConfig: FilterConfigType
};



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
            results[fullMetricName] = []
        }
        results[fullMetricName][epoch] = { ...results[fullMetricName][epoch], [eId]: metricScore.score }
    }

    for (const lossScore of lossScores) {
        const fullLossName = lossScore.split + "/" + lossScore.loss
        if (!results[fullLossName]) {
            results[fullLossName] = []
        }
        results[fullLossName][epoch] = { ...results[fullLossName][epoch], [eId]: lossScore.score }
    }

    // format : {metric_key_1: [{experiment_id_1: score_x, experiment_id_2: score_y, ... }, {}, ...]}
    return results
}, {});

export const filteredModelEvaluationSelector = (state: RootState, metricFilterRegex: string) => {
    // results: {experiment_id_1: [0.9, 0.3, ...]}
    const results = modelEvaluationSelector(state)

    var regex = new RegExp(metricFilterRegex);
    var filteredResults = Object.keys(results).filter(scoreKey => regex.test(scoreKey)).reduce((obj: any, key) => {
        return { ...obj, [key]: results[key] }
    }, {})
    return filteredResults;
};

type EvaluationLineChartPropsType = {
    scoreKey: string
    scoreResult: any;
    experimentIds: Array<string>;
}

type EvaluationChartLinePropsType = {
    dataKey: string;
    lineColor: string;
}

const EvaluationChart: React.FC<EvaluationLineChartPropsType> = ({ scoreKey, scoreResult, experimentIds }) => {

    const lines = experimentIds.map((eID, index) => <Line
        dataKey={eID}
        stroke={selectColor(index)}
    />)

    return (
        <div id="analysis-board-container">
            <div>{scoreKey}</div>
            <LineChart
                width={500}
                height={300}
                data={scoreResult}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {lines}
            </LineChart>
        </div>
    )
}



const AnalysisBoard: React.FC<AnalysisBoardProps> = ({ filterConfig }) => {

    // const metricFilters = ["train/F1_SCORE_macro", "val/F1_SCORE_macro", "test/F1_SCORE_macro",
    //     "train/PRECISION_macro", "val/PRECISION_macro", "test/PRECISION_macro",
    //     "train/RECALL_macro", "val/RECALL_macro", "test/RECALL_macro"]

    // const experimentIds = ["0", "1"]

    const scoreResults = useAppSelector((state: RootState) => filteredModelEvaluationSelector(state, filterConfig.metricFilterRegex))
    const scoreKeys: any = Object.keys(scoreResults)
    const experimentIds = Object.keys(scoreResults[scoreKeys[0]][0])

    const charts = scoreKeys.map((scoreKey: any) => <div className="diagram-cell"><EvaluationChart scoreKey={scoreKey} scoreResult={scoreResults[scoreKey]} experimentIds={experimentIds} /></div>)

    return (
        <>
            {/* <h1> Analysis Board </h1> */}
            {charts}
        </>
    );
}

export default AnalysisBoard;