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

export default function handleExperimentStatusData(data: JSON): Experiment {
    const { status, ...rest } = data as ExperimentStatusPayload;
    return { model_status: status, ...rest };
}
