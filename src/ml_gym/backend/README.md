# MLgym Backend

## Template Endpoints


## RESTful API


## Websocket API

Every event message has the following structure:

```json
{"event_type": <event type>, "creation_ts": <unix timestamp (ms)>, "payload": <payload dict>}

```
### Gym

tracks the job status from within Pool.

Job status:
```json
{
    "event_type": "job_status",
    "creation_ts": "1",
    "payload": { 
        "job_id":1,
        "job_type": <CALC, TERMINATE>
        "status": <INIT, RUNNING, DONE>,
        "starting_time": 123,
        "finishing_time": 123,
        "error": "error message",
        "stacktrace": "stacktrace message",
        "device": "GPU"
    }
}
```

Model status:

tracks the model training status from within GymJob.

```json
{
    "event_type": "model_status",
    "creation_ts": "1",
    "payload": { 
        "model_path": "/foo/bar",
    }
}
```

