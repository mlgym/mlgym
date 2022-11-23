import { Epoch, Experiment } from './experimentsSlice';

export interface serverExpriment {
  experiment_id  : string;
  grid_search_id : string;
  [key: string]  : any;
}

export type experimentEvent = "experiment_status" | "evaluation_result" | "experiment_config";

export const convertExperiment = (input: serverExpriment, eType: experimentEvent): Experiment => {
  if (input["experiment_id"] === undefined) throw ("Missing identifier in message 'experiment_id'");

  let result: Experiment = {
    grid_search_id : input.grid_seach_id,
    experiment_id  : input.experiment_id
  }

  switch (eType) {
    /*
    "payload": { 
      "grid_search_id" : <timestamp>, 
      "experiment_id"  : <int>,
      "job_id"         : <int>,
      "config"         : {<YAML config casted to JSON>},
    }
    */
    case "experiment_config": {
      // unhandled.
      console.log ("NANI?!");
    } break;

    /*
    "payload": {
      "epoch": <int>,
      "grid_search_id": <timestamp>, 
      "experiment_id": <int>,
      "metric_scores": [
        {
          "metric": "f1_score", 
          "split": "train",
          "score": 0.9
        }, 
        {...}
      ],
      "loss_scores": [
        {
          "loss": "bce_loss", 
          "split": "train",
          "score": 0.1
        },
        {...}
      ]
    }
    */
    case "evaluation_result": {
      let chart_ids = [];
      let scores = input["metric_scores"];
      if (Array.isArray (scores)) {
        for (let iScore = 0; iScore < scores.length; iScore++) {
          let curScore = scores[iScore];
          let chartID  = `${curScore["split"]}-${curScore["metric"]}`;
          let point: Epoch = { id: input["epoch"], score: curScore["score"] };
          chart_ids.push (chartID);
          result[chartID] = [point];
        }
      }

      result.chart_ids = [ ...new Set (chart_ids) ];
    } break;

    /*
    "payload": { 
      "grid_search_id" : <timestamp>
      "experiment_id"  : <int>
      "status"         : <TRAINING, EVALUATING>
      "num_epochs"     : <int>
      "current_epoch"  : <int>
      "splits"         : string[]
      "current_split"  : string
      "num_batches"    : <int>
      "current_batch"  : <int>
    }
    */
    case "experiment_status": {
      result = {
        experiment_id  : input.experiment_id,
        grid_search_id : input.grid_search_id, 
        status         : input.status,
        num_epochs     : input.num_epochs,
        current_epoch  : input.current_epoch,
        splits         : input.splits,
        current_split  : input.current_split,
        num_batches    : input.num_batches,
        current_batch  : input.current_batch
      }
    } break;

    default: break;
  }

  return result;
}