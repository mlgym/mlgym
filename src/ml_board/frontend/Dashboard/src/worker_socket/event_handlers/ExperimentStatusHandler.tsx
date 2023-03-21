import { Experiment } from "../../redux/experiments/yetAnotherExperimentSlice";

interface ExperimentStatusPayload extends JSON {
    "grid_search_id": string;// "2022-11-23--20-08-38",
    "experiment_id": number; // 6,
    "status": string; // "evaluation",
    "num_epochs": number;// 100,
    "current_epoch": number;// 0,
    "splits": Array<string>; // ["train", "val", "test"],
    "current_split": string;// "train",
    "num_batches": number; // 8400,
    "current_batch": number;// 840
}

// transform JSON data into Experiment:
export default function handleExperimentStatusData(data: JSON): Experiment {
    // 1. key renaming "status" to "model_status"
    // 2. remove grid_search_id
    const { grid_search_id, status, ...rest } = data as ExperimentStatusPayload;
    return {
        model_status: status,
        // 3. (extra) progresses calculating & storing them 
        // splits: splits.join(), // TODO: after extracting splits from data
        // 4. (extra) turn the split array into string
        // TODO: epoch_progress = rest.current_epoch / rest.num_epochs,
        // TODO: batch_progress = rest.current_batch / rest.num_batches,
        ...rest
    };
}