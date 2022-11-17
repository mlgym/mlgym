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
{"event_type": <event_type>, "creation_ts": <unix timestamp (ms)>, "payload": <payload dict>}

```

The `event_type` is set to one of {`job_status`, `experiment_status`, `experiment_config`, `evaluation_result`, `checkpoint`}. A `job_status` event describe the current state of a processing job that is associated with an experiment. `experiment_status` describes the progress of the experiment training and evaluation in terms of epoch progress and batch progress on a given dataset split. `experiment_config` contains the specification of a single experiment, i.e., a single hyperparamter configuration out of the grid search. `evaluation_result` contains the metric and loss scores for a single experiment at a given epoch. A `checkpoint` message comprises the model and optimizer state at a given epoch. 

The `creation_ts` determines the unix timestamp when this message was created in the MLgym backend. Note, that this timestamps deviates from the time the message was actually sent via the websocket.

The `payload` key points to the data specific to the `event_type`, which is introduced next. 


**Job status:**

tracks the job status from within Pool.

```python
{
    "event_type": "job_status",
    "creation_ts": "1",
    "event_id": 1,
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

Each experiment is associated with a job as a one-to-one relationship. The `job_id` uniquely identifies the job. A job can be either of `job_type` `CALC` or `TERMINATE`. A `CALC` job always trains a concrete model, whereas a `TERMINATE` is an empty job telling a process from the pool to exit. A job can be in one of the three `status`es `INIT`, `RUNNING`, and `DONE`. Before the training, a job is initialized in state `INIT`, switches to `RUNNING` once the training starts and switches to `DONE` when the job finishes either due to an error or a successfully executed experiment. Each grid_search comprises a set of experiments. The set of experiments is defined by the different hyperparameter combinations within the grid search specification. Via the tuple (`grid_search_id`, `experiment_id`) we can uniquely identify an experiment across different grid search runs. The `starting_time` and `finishing_time` store the time when the `state` switches from `INIT` to `RUNNING` and from `RUNNING` to `DONE`, respectively. Errors and their stacktrace are stored within `error` and `stacktrace`, respectively. `device` indicates the computation device (e.g., CPU or GPU 1) the job is being executed on.   

**Experiment status**:

tracks the model training status from within GymJob.

```python
{
    "event_type": "experiment_status",
    "creation_ts": "1",
    "event_id": 1,
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
The `experiment_status` message provides udpates regarding the progress of the training/evaluation in terms on epoch and bath progress. The `status` field indicates whether the model is currently training or evaluating. The `num_epochs` and `current_epjoch` field specify the total number of epochs to be run and the currently running epoch, respectively. The `splits` field contains a list dataset splits that we run on. This field depends on the current `status`. During training, we usually only train on the `train` split, in which case the `splits` list only a single element. In contrast, during evaluation, we usually evaluate on all the splits that are available, in which case the splits list would comprise all the different splits, e.g., train, val and test. `num_batches` and `current_batch` determine the number of batches and the currently executed batch within the respective `current_split`, respectively.





**Experiment config**:

specifies the configuration of a single experiment

```python
{
    "event_type": "experiment_config",
    "creation_ts": "1",
    "event_id": 1,
    "payload": { 
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "job_id": <int>,
        "config": {<YAML config casted to JSON>},
    }
}
```
The `experiment_config` message provides the entire experiment setup for a single hyperparamter configuration from the grid search. For an exemplary grid search configuration, see [here](https://github.com/mlgym/mlgym/blob/master/example/grid_search_example/gs_config.yml).


**Model Evaluation**:

metric scores of a model at a specific epoch.

```python
{
    "event_type": "evaluation_result",
    "creation_ts": "1",
    "event_id": 1,
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

The `evaluation_result` message contains the metric and loss scores for a single experiment at a given `epoch`. `metric_scores` contains metric scores for different `metric`s and `split`s. In practic though, the message always only comprises the results w.r.t. a specific split. An evaluation on a different split is ther fore sent within a different message. 

**Checkpointing**:

After each epoch and if condition is fulfilled (based on strategy), the model is binarized and sent to the server as a checkpoint.

Create checkpoint:

```python
{
    "event_type": "checkpoint",
    "creation_ts": "1",
    "event_id": 1,
    "payload": {
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "checkpoint_id": <str>, # the respective epoch
        "checkpoint_streams":{
            "model": <model as binary stream>,
            "optimizer": <optimizer as binary stream>,
            "stateful_components": <stateful components as byte stream>
        }
    }
}
```

The `checkpoint` message comprises the `model`, `optimizer`, and `stateful_components` state at a given epoch, as indicated by the `checkpoint_id`. The state is sent as a base64 converted binary stream. Since the different states can become rather large, we will implement chunking in the future.  



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
        "checkpoint_id": <str>,
        "checkpoint_streams":{
            "model": None,
            "optimizer": None,
            "stateful_components": None
        }
    }
}
```


# Implementation idea: 

Add subscribers to trainer, evaluator and gymjob. We need to inject them via 
For trainer and evaluator we add the subscribers within the blueprints. E.g., trainer.add_subscriber(subscriber)

We add the subscriber constructable to the blueprint via the GridSearchValidator.create_blueprints().

Subscriber constructable that we parameterize within the Gym and then pass down to trainer, evaluator via gymjob. The idea is that the constructable has a unique interface for construction and the constructed object always has the same interface for logging. Due to that we can implement various types of loggers (local, websocket etc.)


