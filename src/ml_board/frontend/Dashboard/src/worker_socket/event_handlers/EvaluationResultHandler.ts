// interface data_evaluation_result {
//     "grid_search_id": "2022-11-23--20-08-38",
//     "experiment_id": 18,
//     "epoch": 0,
//     "metric_scores": [{
//         "metric": "F1_SCORE_macro",
//         "split": "train",
//         "score": 0.04199189495669321
//     }, {
//         "metric": "PRECISION_macro",
//         "split": "train",
//         "score": 0.052925666019545944
//     }, {
//         "metric": "RECALL_macro",
//         "split": "train",
//         "score": 0.100662497082089
//     }],
//     "loss_scores": [{
//         "loss": "cross_entropy_loss",
//         "split": "train",
//         "score": 2.3039234473024095
//     }]
// }

// ============================ Input shape ================================
interface EvaluationResultPayload extends JSON {
    epoch: number,
    grid_search_id: string,
    experiment_id: number,
    metric_scores: Array<Score>,
    loss_scores: Array<Score>
}

interface Score {
    metric?: string,
    loss?: string,
    split: string,
    score: number
}

// ============================ Output shape ===============================
export interface ChartUpdate {
    chart_id: string,
    exp_id: number,
    epoch: number,
    score: number
}

// ============================ Main function ==============================
export default function handleEvaluationResultData(data: JSON) {
    // parse the incoming data to match EvaluationResultPayload
    const parsedData = data as EvaluationResultPayload;
    // to append to experiment values in the charts
    const charts_updates: ChartUpdate[] = [];
    // for saving the latest score values to update the table
    const table_scores: { [latest_split_metric_key: string]: number } = {};

    // loop over the metrics and another over the losses
    for (const scoreObj of parsedData.metric_scores) {
        table_scores[scoreObj.split + "_" + scoreObj.metric] = scoreObj.score;
        charts_updates.push({
            chart_id: scoreObj.split + "_" + scoreObj.metric,
            exp_id: parsedData.experiment_id,
            epoch: parsedData.epoch,
            score: scoreObj.score
        });
    }
    for (const scoreObj of parsedData.loss_scores) {
        table_scores[scoreObj.split + "_" + scoreObj.loss] = scoreObj.score;
        charts_updates.push({
            chart_id: scoreObj.split + "_" + scoreObj.loss,
            exp_id: parsedData.experiment_id,
            epoch: parsedData.epoch,
            score: scoreObj.score
        });
    }

    return { experiment_id: parsedData.experiment_id, charts_updates, table_scores };
}