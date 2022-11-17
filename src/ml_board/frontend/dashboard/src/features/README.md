# Redux Data Structures

In this document, we specify the redux data structures used within the MLboard frontend. Since messages come in frequently, also the react components need to be redrawn at the same rate. 
Therefore, we need data structures that allow for efficient updates of incoming messages and need little to no operations to reshape the data for the visual components. 

## Evaluation Result

The evaluation result messages coming in via the websocket have the following format:

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
A list of these messages is a highly inefficient format when transforming it to the recharts format, as we have to iterate over each message and each epoch. Therefore, we reshape the data already in the correct recharts format at message insert time. 


### Redux Data Structure

```python
evaluation_results: {
        <split_name/score_key_1>: [
            {
                epoch: <int>, 
                <experimint_id_1>:<score_value>,
                <experiment_id_2>:<score_value>,
                ... 
            },
            ...
        ]
        <score_key_2>: [
            ...
        ]
    }

experiment_ids: {
        <experiment_id_1>: True,
        <experiment_id_2>: True, 
        ...,
        <experiment_id_n>: True
    }

score_keys: {
    <score_key_1>: True,
    <score_key_2>: True,
    ...,
    <score_key_m>: True
}

latest_scores : {
    
    <experiment_id_1>: {
        <split_name_x>/<score_key_y>: <score_value>
        <split_name_x>/<score_key_z>: <score_value>
        ...
    }
    ...
    <experiment_id_n>: {
        <split_name_x>/<score_key_y>: <score_value>
    }
}

experiment_id_to_latest_event_id: {
    <experiment_id_1>: <event_id_x>,
    ...
    <experiment_id_n>: <event_id_y>
}


```

Since there is no "Set" implementation in Redux, we define the set of score_keys and experiment_ids as the keys of a dictionary. 

### Complexity

**Insert message complexity:**

O(N), where N is the number of score values to be inserted. 

**Data retrieval complexity of single line chart:**

O(1), given that the elements in `<split_name/score_key_1>` are already sorted

** Data retrieval complexity of single table row**

O(1)



## Job Status

The incoming job status message has the following format:

```python
{
    "event_type": "job_status",
    "creation_ts": "1",
    "event_id": <int>
    "payload": { 
        "job_id":<str>,          # format <grid_search_id>/<job index>
        "job_type": <str>        # <CALC, TERMINATE>
        "status": <str>          # <INIT, RUNNING, DONE>,
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

We have two data structures. The first one manages the state of the latest job_status update. The second dictionary maps the `experiment_id`s to the latest respective `event_id`s. If for some reason the messages don't arrive in a timewise order, 

```python
job_statues: {
    <experiment_id_1>: {
        "event_type": "job_status",
        "creation_ts": "1",
        "event_id": <int>
        "job_id":<str>,          # format <grid_search_id>/<job index>
        "job_type": <str>        # <CALC, TERMINATE>
        "status": <str>          # <INIT, RUNNING, DONE>,
        "grid_search_id": <str>  # <timestamp>, 
        "experiment_id": <int>,
        "starting_time": <unix_timestamp>,
        "finishing_time": <unix_timestamp>,
        "error": <str>,
        "stacktrace": <str>,
        "device": <str>
    }
    ...
    <experiment_id_n>: {
        ...
    }

experiment_id_to_latest_event_id: {
    <experiment_id_1>: <event_id_x>,
    ...
    <experiment_id_n>: <event_id_y>
}
```

**Insert message complexity:**

O(1), since we either replace or keep the data as a whole based on the `event_id`. If we replace the data, we need to update the second dictionary with the new event_id.

**Data retrieval complexity for data table:**
O(N), where N is the number of keys to consider for as columns.


## Experiment Status

The incoming job status message has the following format:

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

### Redux data structure

We have two data structures. The first one manages the state of the latest experiment_status update. The second dictionary maps the `experiment_id`s to the latest respective `event_id`s. If for some reason the messages don't arrive in a timewise order. 

```python
{
    <experiment_id_1>: {
        "grid_search_id": <timestamp>, 
        "experiment_id": <int>,
        "status": <str>         # <TRAINING, EVALUATING>,
        "num_epochs": <int>,
        "current_epoch": <int>,
        "splits": [<str>, ...], # e.g., ["train", "val", "test"],
        "current_split": <str>, # e.g., "val"
        "num_batches": <int>,
        "current_batch": <int>
    }
    ...
    <experiment_id_n>: {
        ...
    }

experiment_id_to_latest_event_id: {
    <experiment_id_1>: <event_id_x>,
    ...
    <experiment_id_n>: <event_id_y>
}
```

**Insert message complexity:**

O(1), since we either replace or keep the data as a whole based on the `event_id`. If we replace the data, we need to update the second dictionary with the new event_id.

**Data retrieval complexity for data table:**
O(N), where N is the number of keys to consider for as columns.