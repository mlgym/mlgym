# Redux Data Structures

In this document, we specify the redux data structures used within the MLboard frontend. Since messages come in frequently, also the react components need to be redrawn at the same rate. 
Therefore, we need data structures that allow for efficient updates of incoming messages and need little to no operations to reshape the data for the visual components. 

## Job Status

The incoming `job_status` message has the following format:

```python
{
    "event_type": "job_status",
    "creation_ts": "1",
    "event_id": <int>
    "payload": { 
        "job_id":<str>,          # format <grid_search_id>-<job index>
        "job_type": <str>        # <CALC, TERMINATE>
        "status": <str>          # <INIT, RUNNING, DONE>
        "grid_search_id": <str>  # <timestamp>, 
        "experiment_id": <int>,
        "starting_time": <unix_timestamp>,
        "finishing_time": <unix_timestamp>,
        "error": <str>,
        "stacktrace": <str>,
        "device": <str>
    }
}
```

### Redux data structure 

Here is how the **jobs slice** is implemented:

```tsx
export interface Job {
  job_id          : string; // format <grid_search_id>-<job index>
  job_type?       : string; // <CALC, TERMINATE>
  status?         : string; // <INIT, RUNNING, DONE>
  grid_search_id? : string; // <timestamp>
  experiment_id?  : string;
  starting_time?  : number;
  finishing_time? : number;
  error?          : string;
  stacktrace?     : string;
  device?         : string;
}

export interface JobsState {
  [jID: string]: Job;
}
```

Here is how the slice looks in the redux state:

```python
jobs: {
    <job_id>: {
        "job_id":<str>,          # format <grid_search_id>-<job index>
        "job_type": <str>        # <CALC, TERMINATE>
        "status": <str>          # <INIT, RUNNING, DONE>
        "grid_search_id": <str>  # <timestamp>, 
        "experiment_id": <str>,
        "starting_time": <number>,
        "finishing_time": <number>,
        "error": <str>,
        "stacktrace": <str>,
        "device": <str>
    }
    ...
    <job_id>: {
        ...
    }
}
```

### Complexity

**Insert message complexity:**

**Data retrieval complexity of single line chart:**

**Data retrieval complexity for data table:**

**Data retrieval complexity of single table row:**







## Evaluation Result & Experiment Status

The `evaluation_result` messages coming in via the websocket have the following format:

```python
{
    "event_type": "evaluation_result",
    "creation_ts": <unix timestamp>,
    "event_id": <int>
    "payload": {
        "epoch": <int>,
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "metric_scores": [
            {
                "metric": <str>, 
                "split": <str>,
                "score": <float>
            }, 
            ...
        ],
        "loss_scores": [
            {
                "loss": <str>,, 
                "split": <str>,,
                "score": <float>
            },
            ...
        ]
    }
}
```

The incoming `experiment_status` message has the following format:

```python
{
    "event_type": "experiment_status",
    "creation_ts": "1",
    "event_id": <int>
    "payload": { 
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "status": <str> # <TRAINING, EVALUATING>,
        "num_epochs": <int>,
        "current_epoch": <int>,
        "splits":  [<str>, ...], # e.g., ["train", "val", "test"],
        "current_split": <str>, # e.g., "val"
        "num_batches": <int>,
        "current_batch": <int>
    }
}
```
It's highly inefficient to store every message as is, and traverse through all of them to render the charts. Hence, the messages are parsed the moment they are received, and saved into experiments slice in the redux state.

### Redux data structure

Here is how the **experiments slice** is implemented:

```tsx
export interface Epoch {
  id            : number;
  [eID: string] : number;
}

export interface Experiment {
  grid_search_id : string; 
  experiment_id  : string;
  chart_ids?     : string[]; //format ${split}@@${metric}
  status?        : string;   // <TRAINING, EVALUATING>,
  current_split? : string;
  splits?        : string[]; //e.g.: ["train", "val", "test"],
  num_epochs?    : number;
  current_epoch? : number;
  num_batches?   : number;
  current_batch? : number;
  color?         : string;
  // used to keep split data -- VV    To avoid compilation error      VV
  [split_metric: string] : Epoch[] | number | string | string[] | undefined;
  // -------------------------- ^^^^^^ To avoid compilation error ^^^^^^
}

export interface ExperimentsState {
  [eID: string]: Experiment;
}
```

Here is how the slice looks in the redux state:

```python
experiments: {
    <experiment_id>: {
        "grid_search_id": <str>, # is a timestamp
        "experiment_id": <str>,  # e.g.: 0,1,2,...
        "status": <str>          # <TRAINING, EVALUATING>,
        "num_epochs": <int>,
        "current_epoch": <int>,
        "splits": [<str>, ...], # e.g.: ["train", "val", "test"],
        "current_split": <str>, # e.g.: "val"
        "num_batches": <int>,
        "current_batch": <int>,
        "color": <str>,
        "chart_ids": [<str>, ...], # format ${split}@@${metric}
        [<split_metric>]:  [
          {
            <experiment_id>: <float>,
            id: <int>
          },
          ...
        ],
    }
    ...
    <experiment_id>: {
        ...
    }
}
```

### Complexity

**Insert message complexity:**

**Data retrieval complexity of single line chart:**

**Data retrieval complexity for data table:**

**Data retrieval complexity of single table row:**
