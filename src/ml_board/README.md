# MLboard

MLboard is a solution for tracking model training progress, logging evaluations and respective models. The package comes with a frontend to visualize these different aspects.   

## General structure

The central backend server based on a REST API and a websocket API acts as a hub between MLgym message publishers (log training progress, evaluations and job statuses) and message subscribers (e.g., frontend). 

The backend server uses event sourcing meaning, the history of all messages describing the system at any point in time are being recorded and can be played back to the subscribers. This way, a newly connected client can consume all the training progress messages, even if the training has already started. 

## Getting started

To run the websocket server run 

```sh
cd src/ml_gym/backend/streaming
python websocket_server.py
```

To run the frontend 

```sh
cd src/ml_gym/frontend/dashboard
yarn start
```

Now we can run model training that is being streamed live to the frontend

```sh
cd example/
sh train_gs_mnist_conv_net_websocket.sh
```

The messages received by the websocket server can be analyzed in `event_storage/`

## Template Endpoints


## RESTful API


**Raw Configuration Files**

e.g., grid search or evaluation YAML config

*GET /grid_searches/<grid_search_id>/<config_file_name>*


*PUT /grid_searches/<grid_search_id>/<config_file_name>*

payload:
```json
{   
    file_format: <e.g., YAML>
    content: <YAML file as string>
}
```

**Experiments**

*GET /grid_searches/<grid_search_id>/experiments*

```json
[
    {
        "experiment_id": <int>,
        "last_checkpoint_id": <int>,
        "experiment_config": <config_dict>
    },
    {
        ...
    }
]
```

**Checkpoints**

*GET /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>*


```json
{
        "model": <binary stream>,
        "optimizer": <binary stream>,
        "stateful_components": <binary stream>
}

```

*GET /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>/model*

*GET /checkpoints/<grid_search_id>/<experiment_id><checkpoint_id>/optimizer*

*GET /checkpoints/<grid_search_id>/<experiment_id><checkpoint_id>/stateful_component*


## Websocket API

Every event message has the following structure:

```json
{"event_type": <event type>, "creation_ts": <unix timestamp (ms)>, "payload": <payload dict>}

```

**Job scheduled:**

Dispatched when a job is scheduled within the gym

```json
{
    "event_type": "job_scheduled",
    "creation_ts": "1",
    "payload": { 
        "job_id": 1,
        "config": <YAML config as JSON for a single model, i.e., one single instance of the grid search>
    }
}
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
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
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
    "event_type": "experiment_status",
    "creation_ts": "1",
    "payload": { 
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "status": <TRAINING, EVALUATING>,
        "num_epochs": 200,
        "current_epoch": 102,
        "splits": ["train", "val", "test"],
        "current_split": "val",
        "num_batches": 1052,
        "current_batch": 59
    }
}
```

**Experiment config**:

specifies the configuration of a single experiment

```json
{
    "event_type": "experiment_config",
    "creation_ts": "1",
    "payload": { 
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "job_id": <int>,
        "config": {<YAML config casted to JSON>},
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
}
```

**Checkpointing**:

After each epoch and if condition is fulfilled (based on strategy), the model is binarized and sent to the server as a checkpoint.

Create checkpoint:

```json
{
    "event_type": "checkpoint",
    "creation_ts": "1",
    "payload": {
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "checkpoint_id": <int>, # epoch
        "entity_id": <str> # <model, optimizer, stateful_components>
        "chunk_data": <chunk of binary stream>,
        "chunk_id": <int> # id identifying the chunk,
        "final_num_chunks": <int> # 
    }
}
```

The files received by the websocket server are stored in 
`event_storage/mlgym_event_subscribers/<grid_search_id/event_storage_id><experiment_id>/checkpointing/<checkpoint_id>` as `model.pt`, `optimizer.pt` and `stateful_components.pt`. These files are available via the RESTful API to the clients and are not streamed.

Delete checkpoint:

```json
{
    "event_type": "checkpoint",
    "creation_ts": "1",
    "payload": {
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "checkpoint_id": <int>, # epoch
        "entity_id": <str> # <model, optimizer, stateful_components>
        "chunk_data": None,
        "chunk_id": -1,
        "final_num_chunks": 0 
    }
}
```


# Implementation idea: 

Add subscribers to trainer, evaluator and gymjob. We need to inject them via 
For trainer and evaluator we add the subscribers within the blueprints. E.g., trainer.add_subscriber(subscriber)

We add the subscriber constructable to the blueprint via the GridSearchValidator.create_blueprints().

Subscriber constructable that we parameterize within the Gym and then pass down to trainer, evaluator via gymjob. The idea is that the constructable has a unique interface for construction and the constructed object always has the same interface for logging. Due to that we can implement various types of loggers (local, websocket etc.)


