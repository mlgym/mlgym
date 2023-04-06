# Redux Data Structures

In this section, we specify the redux data structures used within the MLboard frontend.

We will be taking `evaluation_result` as an example to show the process.

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

The messages from websocket are handled by event handlers stored in `path: src/websocket/event_handlers`. For Experiment Results, we have `handleExperimentStatusData`. Here we take the previous redux state, restructure the new data, update the previous redux state and make it ready to be stored/updated in redux.<br/>
This restructuring is happening in a thread seperate from UI thread.<br/>
Here, the redux data is structured as follows:

```python
    {
        "ExperimentsReducer": {
            "evalResult": {
                "grid_search_id": <str>,
                "experiments": {
                    [split]_[metric]: {
                        "data": {
                            "labels": <list>,
                            "datasets": [
                                "exp_id": <int>,
                                "label": <str>,
                                "data": <list>
                                "fill": <bool>,
                                "backgroundColor": <str>,
                                "borderColor": <str>
                            ]
                        },
                        "options": {
                            "plugins": {
                                "title": {
                                    "display": <bool>,
                                    "text": <str>,
                                    "color": <str>,
                                    "font": {
                                        "weight": <str>,
                                        "size": <str>
                                    }
                                }
                            }
                        },
                        "ids_to_track_and_find_exp_id": <list>
                    },
                    [split]_[loss]: {
                        "data": {
                            "labels": <list>,
                            "datasets": [
                                "exp_id": <int>,
                                "label": <str>,
                                "data": <list>
                                "fill": <bool>,
                                "backgroundColor": <str>,
                                "borderColor": <str>
                            ]
                        },
                        "options": {
                            "plugins": {
                                "title": {
                                    "display": <bool>,
                                    "text": <str>,
                                    "color": <str>,
                                    "font": {
                                        "weight": <str>,
                                        "size": <str>
                                    }
                                }
                            }
                        },
                        "ids_to_track_and_find_exp_id": <list>
                    }
                }
            }
        }
    }
```

We would loop over metric_scores & loss_scores and get all the split-metric & split-loss pairs and add all the new pairs to experiment dict. If the pair is already present, then we update it with new or existing experiment_ids.<br/>

Each pair has 3 dicts - data, options, ids_to_track_and_find_exp_id.<br/>

Here, data & options are structured as per the react-chartjs-2 library needs the data. So, keeping such structure in redux itself will help in redering the data by directly accessing redux state without any prepocessing.<br/>

Labels are the range of min to max epochs. Datasets are the list of each experiment data & properties for react-chartjs-2 library.<br/>

ids_to_track_and_find_exp_id array is used to keep track of experiments present at a certain index in data->datasets dict. So that we can update the [split]-[metric_OR_loss]->data->datasets->[exp_index]->data array when we encounter an experiment_id which is already present.<br/>

options are used for setting styling the title of the chart. It is structured as per the requirements of the react library.<br/>

Then `handleExperimentStatusData` returns the whole updated redux sate back to the SocketClass, which will invoke the callback function (`dataCallback`) of the `worker.js` - `workerOnMessageCallback`. This method will invoke the postMessage API which will send the data from webworker to UI (here, to `AppNew.js`).

In `AppNew.js`, the messages from webworkers are handled in `workerOnMessageHandler`. From this method, we save the dict directly into redux using the method: `this.props.saveEvalResultData(data);`