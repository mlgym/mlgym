# MLgym Backend

## Template Endpoints


## RESTful API


## Websocket API

Every event message has the following structure:

```json
{"event_type": <event type>, "creation_ts": <unix timestamp (ms)>, "payload": <payload dict>}

```

**Job status:**

tracks the job status from within Pool.

```json
{
    "event_type": "job_status",
    "creation_ts": "1",
    "payload": { 
        "job_id":1,
        "job_type": <CALC, TERMINATE>
        "status": <INIT, RUNNING, DONE>,
        "model_id": <path_to_model>
        "starting_time": 123,
        "finishing_time": 123,
        "error": "error message",
        "stacktrace": "stacktrace message",
        "device": "GPU"
    }
}
```

**Model status**:

tracks the model training status from within GymJob.

```json
{
    "event_type": "model_status",
    "creation_ts": "1",
    "payload": { 
        "model_id": <path to model>,
        "status": <TRAINING, EVALUATING>,
        "current_epoch": 102,
        "splits": ["train", "val", "test"],
        "current_split": "val",
        "split_progress": 59
    }
}
```

**Model Evaluation**:

metric scores of a model at a specific epoch.

```json
{
    "event_type": "evaluation_result",
    "creation_ts": "1",
    "payload": {
        "epoch": 100,
        "model_id": <path to model>,
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
                "metric": "bce_loss", 
                "split": "train",
                "score": 0.1
            },
            {...}
        ]
    }
}
```