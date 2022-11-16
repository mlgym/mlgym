import "./analysis_board.css";

import React from "react";
import {
    CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis,
    YAxis
} from "recharts";
import { FilterConfigType, ModelEvaluationPayloadType, ModelEvaluationType } from "../app/datatypes";
import { useAppSelector } from "../app/hooks";
import type { RootState } from '../app/store';


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

    const { epoch, experiment_id: eId, loss_scores: lossScores, metric_scores: metricScores } = modelEvaluationPayload
    // const epoch = modelEvaluationPayload.epoch
    // const eId = modelEvaluationPayload.experiment_id
    // const lossScores = modelEvaluationPayload.loss_scores
    // const metricScores = modelEvaluationPayload.metric_scores

    for (const metricScore of metricScores) {
        const fullMetricName = metricScore.split + "/" + metricScore.metric
        if (!results[fullMetricName]) {
            results[fullMetricName] = {}
        }
        if (!results[fullMetricName][epoch])
            results[fullMetricName][epoch] = { name: epoch }
        results[fullMetricName][epoch] = { ...results[fullMetricName][epoch], [eId]: metricScore.score }
    }

    for (const lossScore of lossScores) {
        const fullLossName = lossScore.split + "/" + lossScore.loss
        if (!results[fullLossName]) {
            results[fullLossName] = {}
        }
        if (!results[fullLossName][epoch])
            results[fullLossName][epoch] = { name: epoch }
        results[fullLossName][epoch] = { ...results[fullLossName][epoch], [eId]: lossScore.score }
    }

    // format : {metric_key_1: [{experiment_id_1: score_x, experiment_id_2: score_y, ... }, {}, ...]}



    return results
}, {});

export const sortedModelEvaluationSelector = (state: RootState) => { // sorts the scores by epoch so that they are plotted in the correct order within the line charts
    const results: any = modelEvaluationSelector(state)

    var resultsSorted = Object.keys(results).reduce((tmpResult, scoreKey) => {
        return {
            ...tmpResult, [scoreKey]: Object.keys(results[scoreKey]).sort(function (a, b) { return parseInt(a) - parseInt(b); }).reduce((scoreResult: any, epochKey) => {
                return [...scoreResult, results[scoreKey][epochKey]]
            }, [])
        };
    }, {})

    return resultsSorted;
}

export const filteredModelEvaluationSelector = (state: RootState) => {
    // results: {experiment_id_1: [0.9, 0.3, ...]}
    const results: any = sortedModelEvaluationSelector(state);
    const re = new RegExp(state.RegEx.value)
    var filteredResults = Object.keys(results).filter(scoreKey => re.test(scoreKey)).reduce((obj: any, key) => {
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

    const lines = experimentIds.map((eID: string, index: number) => <Line
        dataKey={eID}
        stroke={selectColor(index)}
        key={"line#" + index}
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

    const scoreResults = useAppSelector((state: RootState) => filteredModelEvaluationSelector(state))
    const scoreKeys: any = Object.keys(scoreResults)
    const experimentIds = Object.keys(scoreResults[scoreKeys[0]][0]).filter(function (item) { return item !== "name" })

    const charts = scoreKeys.map((scoreKey: any) =>
        <div className="diagram-cell">
            <EvaluationChart key={scoreKey} scoreKey={scoreKey} scoreResult={scoreResults[scoreKey]} experimentIds={experimentIds} />
            </div>)


    return (
        <>
            {/* <h1> Analysis Board </h1> */}
            {charts}
        </>
    );
}

export default AnalysisBoard;