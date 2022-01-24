# MLgym Backend

## Template Endpoints


## RESTful API


## Websocket API

Every event message has the following structure:

```json
{"event_id": 1, "payload": <payload dict>}

```
### Gym

tracks the job status from within Pool.

Job status:
```json
{
    "event_type": "job_status", 
    "job_id":1,
    "job_type": <CALC, TERMINATE>
    "status": <INIT, RUNNING, DONE>,
    "starting_time": 123,
    "finishing_time": 123,
    "error": "error message",
    "stacktrace": "stacktrace message",
    "device": "GPU"
}
```

Model status:

tracks the model training status from within GymJob.

```json
{
    "event_type": "model_status", 
    "model_path": "/foo/bar",

}
```

