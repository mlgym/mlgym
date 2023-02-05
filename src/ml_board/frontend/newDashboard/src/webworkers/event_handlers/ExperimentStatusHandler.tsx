import { Experiment } from "../../redux/experiments/yetAnotherExperimentSlice";

// interface data_experiment_status {
//     "grid_search_id": "2022-11-23--20-08-38",
//     "experiment_id": 6,
//     "status": "evaluation",
//     "num_epochs": 100,
//     "current_epoch": 0,
//     "splits": ["train", "val", "test"],
//     "current_split": "train",
//     "num_batches": 8400,
//     "current_batch": 840
// }
export default function handleExperimentStatusData(data: any): Experiment {
    data.model_status = data.status;
    delete data.status
    return data;
}
