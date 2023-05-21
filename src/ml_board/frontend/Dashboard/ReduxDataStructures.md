# Redux Data Structures

In this document, we specify the redux data structures used within the MLboard frontend. Since messages come in frequently, and the react components need to be redrawn at a close rate. 
Therefore, we need data structures that allow for efficient updates of incoming messages and need little to no operations to reshape the data for the visual components. 

The store is divided mainly into 3 slices, as shown, and each are explained further in this document.
```python
{
    globalConfig: {},
    charts: {},
    table:  {}
}
```

## Global Config Slice

This slice holds the global configurations of the whole app. Here is how it's implemented and its default initial state:

```ts
export interface GlobalConfig {
    currentFilter: string; // the current value of the filter
    idTab: string; // the current open tab
    wsConnected: boolean; // websocket connection flag
    ping: number; // in milliseconds to measure the Round Trip Time
    received_msg_count: number; // total number of messages received from the websocket server 
    throughput: number; // measuring how many messages are received per specific time interval
    grid_search_id: string; // holding the grid_search_id that this client instance is tracking
    table_headers: Array<string>; // all the columns' headers of the table
    rest_api_url: string; // the link used to talk with the REST server
}

const initialState: GlobalConfig = {
    currentFilter: '.*',
    idTab: "analysisboard", 
    wsConnected: false,
    ping: -1,
    received_msg_count: 0,
    throughput: 0,
    grid_search_id: "",
    table_headers: [], 
    rest_api_url: ""
};
```
**Data complexity insertion & retrieval:**  
for every field in this data structure there is a direct getter and setter, so for all of them the Read/Write process is $O(1)$.

### Note!
The following 2 slices were implemented using [createEntityAdapter](https://redux-toolkit.js.org/api/createEntityAdapter) to be in a [Normalized State Shape](https://redux.js.org/usage/structuring-reducers/normalizing-state-shape), that means the slice or the entity state (as RTK name it) structure that looks like:

```ts
{
  // The unique IDs of each item. Must be strings or numbers
  ids: []
  // A lookup table mapping entity IDs to the corresponding entity objects
  entities: {
  }
} 
```

## Table Slice
The final form of the table slice looks like the snippet directly below, then follows a detailed explaination of how this is achived.
```python
{
    table: {
        ids: [ <row_id>, ... ],
        entities: {
            <row_id>: {
                experiment_id: <row_id>,
                job_status: <str>, # <INIT, RUNNING, DONE>
                job_id: <str>, # format <grid_search_id>-<job index>
                job_type: <int>, # <CALC, TERMINATE>
                starting_time: <float>,
                finishing_time: <float>,
                device: <str>, # e.g.: 'cuda: 2',
                error: <str>, 
                stacktrace: <str>, 
                model_status: <str>, # <TRAINING, EVALUATING>
                splits: <str>, # e.g.: "train,val,test",
                epoch_progress: <float>,
                batch_progress: <float>,
                num_epochs: <int>,
                current_epoch: <int>,
                current_split: <str>, # e.g.: "train",
                num_batches: <int>,
                current_batch: <int>,
                ...,
                ...,
                <other_scores>
            },
            ...
        }
    }
}
```
As you can see the table slice is holding the IDs of all the Rows inside of an array conveniently named `ids`.
All these IDs are primary keys for the actual Row entities themselves inside the dictionary named `entities`.
The implementation of the Row entity is actually quite simple, it is just an object that must have an `experiment_id` to function as the primary key for that row in the table.
But it also accept the other fields that are mainly the payloads from the `job_status` and the `experiment_status` mlgym events

```ts
// NOTE: Row = JobStatusPayload + ExperimentStatusPayload + scores
export interface Row {
    // // // Job Payload
    // job_id?: string; // format <grid_search_id>-<job index>
    // job_type?: string; // <CALC, TERMINATE>
    // job_status?: string; // <INIT, RUNNING, DONE>
    // starting_time?: number;
    // finishing_time?: number;
    // error?: string;
    // stacktrace?: string;
    // device?: string;
    
    // // // Experiment Payload
    experiment_id: number;
    // model_status?: string;   // <TRAINING, EVALUATING>,
    // current_split?: string;
    // splits?: string; //e.g.: ["train", "val", "test"],
    // num_epochs?: number;
    // current_epoch?: number;
    // num_batches?: number;
    // current_batch?: number;
    // // progresses calculations
    // epoch_progress?: number;
    // batch_progress?: number;

    // // // and any other field (for different kinds of scores)


    // // NOTE: All of the above could have been written in typescript like this:
    // // [newKey: string]: number | string;
    // // where newKey encompasses all of the above and more if need be!!!
    // // But unfortunately it creates errors if used! (exposing only experiment_id is the current fix)
}
```

For clarification purposes, here is also how the payloads of `job_status` and `experiment_status` mlgym events are parsed:
<table>
<tr>
<th> job_status (with example values)</th>
<th> experiment_status (with example values)</th>
</tr>
<tr>
<td>

```ts
interface JobStatusPayload extends JSON {
    "job_id": string; // "2022-11-23--20-08-38-17",
    "job_type": string; // 1,
    "status": string; // "RUNNING",
    "grid_search_id": string; // "2022-11-23--20-08-38",
    "experiment_id": number; //  17,
    "starting_time": number; // 1669234123.8701758,
    "finishing_time": number; // -1,
    "device": string; // "cuda:4",
    "error": string; // null,
    "stacktrace": string; // null
}
```

</td>
<td>

```ts
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
```

</td>
</tr>
</table>

## Charts Slice

For the last slice it's a bit helpful if you saw or at least understand the main plot behind the film [Inception 2010](https://www.imdb.com/title/tt1375666/), instead of a dream within a dream, here we have mulitple EntityAdapters inside a big EntityAdapter! Take a look at the snippet first then scroll down for futher explaination.

```python
{
    charts: {
        ids: [ <chart_id>, ...],
        entities: {
            <chart_id>: {
                chart_id: <chart_id>,
                x_axis: [ 0, 1, 2, ... ],
                experiments: {
                    ids: [ <experiment_id>, ...],
                    entities: {
                        <experiment_id>: {
                            exp_id: <experiment_id>,
                            data: [ ... ]
                        },
                        ...
                    }
                }
            },
        }
    },
}
```

The idea is we have different Charts, and so there is a dedicated slice to hold all of them. This slice is in a Normalized State Shape, so all the chart entities are saved in a dictionary for fast access and all the keys are also stored in an array called ids.
Now every Chart has its own chart_id, x_axis values (Epochs) and of course contains a specific set of Experiments, hence the other EntityAdaptors inside of it.
By now you surely got the idea of Normalized State Shape, so it's enough to say that the each Experiment contain it's experiment_id and the values at each epoch (values on the y_axis).

The incoming payload of the `evaluation_result` mlgym event:
```ts
interface EvaluationResultPayload extends JSON {
    epoch: number, // string, // in Graph.tsx parsing: false, 
    grid_search_id: string,
    experiment_id: number,
    metric_scores: Array<Score>,
    loss_scores: Array<Score>
}

interface Score {
    metric?: string,
    loss?: string,
    split: string,
    score: number
}
```

is then parsed into `Array<ChartUpdate>`:

```ts
export interface ChartUpdate {
    chart_id: string,
    exp_id: number,
    epoch: number, //string, // in Graph.tsx parsing: false, 
    score: number
}
```

### Complexity
As you might imagine because of the nomalization the data is flat, and we are using sorted array for ids and a dictionary or a hashmap for the entities themselves, so we have a very performant CRUD system.

- table slice has complexity of $O(1)$ for insertion and lookup.
- charts slice has complexity of $O(1)$ for inserting and looking up the chart itself.
- experiment slices inside a chart also has complexity of $O(1)$ for insertion and lookup, as long as we look for a specific exepriment with its experiment_id or retriving all the experiments all together (and this is the current state of the code, exposing only these specific methods).

+note: to update the Charts with the `Array<ChartUpdate>` we definitely use a loop, but this is so far un-avoidable to go over the array, yet a single `ChartUpdate` in itself is done in $O(1)$.

**So the final view of the whole redux store looks like:**
```python
{
    status: {
      currentFilter: <str>, # default: '.*',
      idTab: <str>, # default: "Dashboard"
      wsConnected: <bool>, # default: false,
      ping: <int>, # default: -1
      received_msg_count: <int>, # default: 0
      throughput: <int>, # default: 0
      grid_search_id: <str>, # default: ""
      table_headers: [], # default: []
      rest_api_url: <str> # default: 'http://127.0.0.1:5001'
    },

    charts: {
        ids: [ <chart_id>, ...],
        entities: {
            <chart_id>: {
                chart_id: <chart_id>,
                x_axis: [ 0, 1, 2, ... ],
                experiments: {
                    ids: [ <experiment_id>, ...],
                    entities: {
                        <experiment_id>: {
                            exp_id: <experiment_id>,
                            data: [ ... ]
                        },
                        ...
                    }
                }
            },
        }
    },

    table: {
        ids: [ <row_id>, ... ],
        entities: {
            <row_id>: {
                experiment_id: <row_id>,
                job_status: <str>, # <INIT, RUNNING, DONE>
                job_id: <str>, # format <grid_search_id>-<job index>
                job_type: <int>, # <CALC, TERMINATE>
                starting_time: <float>,
                finishing_time: <float>,
                device: <str>, # e.g.: 'cuda: 2',
                error: <str>, 
                stacktrace: <str>, 
                model_status: <str>, # <TRAINING, EVALUATING>
                splits: <str>, # e.g.: "train,val,test",
                epoch_progress: <float>,
                batch_progress: <float>,
                num_epochs: <int>,
                current_epoch: <int>,
                current_split: <str>, # e.g.: "train",
                num_batches: <int>,
                current_batch: <int>,
                ...,
                ...,
                <other_scores>
            },
            ...
        }
    }
}
```
