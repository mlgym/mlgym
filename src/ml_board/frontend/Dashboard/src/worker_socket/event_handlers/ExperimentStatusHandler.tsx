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
export interface ExperimentStatusRefinedPayload {
    experiment_id: number;
    model_status: string;   // <TRAINING, EVALUATING>,
    current_split: string;
    splits: string; //e.g.: ["train", "val", "test"],
    num_epochs: number;
    current_epoch: number;
    num_batches: number;
    current_batch: number;
}

export default function handleExperimentStatusData(expData: any): ExperimentStatusRefinedPayload {
    // key renaming
    expData.model_status = expData.status;
    delete expData.status

    // remove grid_search_id
    delete expData.grid_search_id

    // turn the split array into string
    expData.splits = expData.splits.join();

    // progresses calculating & storing them 
    expData.epoch_progress = expData.current_epoch / expData.num_epochs;
    expData.batch_progress = expData.current_batch / expData.num_batches;

    return expData;
}
