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

type EvaluationLineChartPropsType = {
    metricFilter: string
    experimentIds: Array<string>;
}

type EvaluationChartLinePropsType = {
    dataKey: string;
    lineColor: string;
}

const EvaluationChart: React.FC<EvaluationLineChartPropsType> = ({ metricFilter, experimentIds }) => {

    const metricSelector = useAppSelector((state: RootState) => filteredModelEvaluationSelector(state, metricFilter))

    const lines = experimentIds.map((eID, index) => <Line
        dataKey={eID}
        stroke={selectColor(index)}
    />)

    return (
        <div id="analysis-board-container">
            <div>{metricFilter}</div>
            <LineChart
                width={500}
                height={300}
                data={metricSelector}
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

    const metricFilters = ["train/F1_SCORE_macro", "val/F1_SCORE_macro", "test/F1_SCORE_macro",
        "train/PRECISION_macro", "val/PRECISION_macro", "test/PRECISION_macro",
        "train/RECALL_macro", "val/RECALL_macro", "test/RECALL_macro"]

    const experimentIds = ["2022-04-29--22-25-49/conv_net/0", "2022-04-29--22-25-49/conv_net/1"]

    var regex = new RegExp(filterConfig.metricFilterRegex);
    const selectedMetricFilters = metricFilters.reduce((selected: Array<string>, metricFilter: string) => {
        if (regex.test(metricFilter))
            selected.push(metricFilter)
        return (selected)
    }, []);

    const charts = selectedMetricFilters.map((metricFilter: string) => <div className="diagram-cell"><EvaluationChart metricFilter={metricFilter} experimentIds={experimentIds} /></div>)

    return (
        <>
            {/* <h1> Analysis Board </h1> */}
            {charts}
        </>
    );
}

export default AnalysisBoard;