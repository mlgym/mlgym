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

_GET /grid_searches/<grid_search_id>/<config_file_name>_

Return:

```
<YAML file as string>
```

_GET /grid_searches/<grid_search_id>/<experiment_id>/<config_file_name>_

Return:

```
<JSON file as string>
```

_PUT /grid_searches/<grid_search_id>/<config_file_name>_

_PUT /grid_searches/<grid_search_id>/<experiment_id>/<config_file_name>_

payload:

```json
{
    "file_format": <e.g. YAML>,
    "content": <YAML file as string>
}
```

**Experiments**

_GET /grid_searches/<grid_search_id>/experiments_

TODO need to check "experiments" in URL

TODO need to check "experiments" in URL  
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

**Checkpointing**

Available <checkpoint_resource> = [model, optimizer, stateful_component, lr_scheduler]

Get all Checkpoint names for single experiment:

_GET /checkpoints/<grid_search_id>/<experiment_id>_

_Ex: GET /checkpoints/2023-04-12--23-42-17/0_

Get all Checkpoint names for single epoch in an experiment:

_GET /checkpoints/<grid_search_id>/<experiment_id>/<checkpoint_id>_

_Ex: GET /checkpoints/2023-04-12--23-42-17/0/0_

Return:
```json
[
    {
        "experiment_id": <experiment_id>,
        "epoch": <checkpoint_id>,
        "checkpoints": [<checkpoint_resource_name>,..]
    }
]

```

Get Checkpoint Resource:

_GET /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>/<checkpoint_resource>_

_Ex: GET /checkpoints/2023-04-12--23-42-17/0/0/model_

Return:

```
<binary stream>
```

Insert Checkpoint Resources:

_POST /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>/<checkpoint_resource>_

_Ex: POST /checkpoints/2023-04-12--23-42-17/0/0/model_

payload:

```json
{
    "data": <binary stream>,
    "msg": "insert checkpoint",
    "type": "multipart/form-data"
}
```

Delete Checkpoint Resources: _model, optimiyer, stateful_component and lr_scheduler_ for a checkpoint ID in the experiment :

_DELETE /checkpoints/<grid_search_id>/<experiment_id>/<checkpoint_id>_

_Ex: DELETE /checkpoints/2023-04-12--23-42-17/0/0_

Delete specific Checkpoint Resource:

_DELETE /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>/<checkpoint_resource>_

_Ex: DELETE /checkpoints/2023-04-12--23-42-17/0/0/model_

*PUT /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>/<model, optimizer, lr_scheduler, stateful_component>*
```json
{
        "<model, optimizer, lr_scheduler, stateful_component>": <binary stream>,
        "chunk_id": <chunk_id>,
        "num_chunks": <num_chunks>
```

*DELETE /checkpoints/<grid_search_id><experiment_id>/<checkpoint_id>*


## Websocket API

Every event message has the following structure:

```json
{"event_type": <event type>, "creation_ts": <unix timestamp (ms)>, "payload": <payload dict>}

```

Historical events are sent as bacthed_events when a new client asks for events:

```json
{"event_type": "batched_events", "data": <array_of_events>}

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

# Implementation idea:

**Checkpointing (legacy)**:

After each epoch and if condition is fulfilled (based on strategy), the model is binarized and sent to the server as a checkpoint.

Create checkpoint:

Add subscribers to trainer, evaluator and gymjob. We need to inject them via
For trainer and evaluator we add the subscribers within the blueprints. E.g., trainer.add_subscriber(subscriber)

We add the subscriber constructable to the blueprint via the GridSearchValidator.create_blueprints().

Subscriber constructable that we parameterize within the Gym and then pass down to trainer, evaluator via gymjob. The idea is that the constructable has a unique interface for construction and the constructed object always has the same interface for logging. Due to that we can implement various types of loggers (local, websocket etc.)
