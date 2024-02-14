# Web-Workers

In this project, we have used web-workers which gives us the advantage of working on the tasks seperately from the main UI thread.<br/>

Initialising the WebSocket in the main thread would slow down the website and make it feel laggy since constantly it would be handling the server data that is pushed in through the WebSocket.<br/>

One way to do this efficiently is by initialising the WebSocket inside a WebWorker. WebWorker does not execute in the main thread instead it will be executed in a separate thread in parallel to the main thread which handles the rendering and handling of user actions.

To get a detailed understanding of these two Web API’s you can go through the following:<br/><br/>

WebSockets — https://blog.logrocket.com/websockets-tutorial-how-to-go-real-time-with-node-and-react-8e4693fbf843/ <br/><br/>

WebWorkers:<br/>
Video — https://youtu.be/Gcp7triXFjg <br/>
Blog — https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API <br/><br/>

Main point is that after creating the worker, an `onmessage` callback listener must be initialized to receive communication when the worker sends messages through `postMessage`, and vice versa.

We will be getting streamable data from the our endpoint (can be localhost or a custom url).

The code to achieve this is split across multiple files:

## App.js
`path: ./src/app/App.js` <br/><br/>
- Here, from within `useEffect` we create a `Worker` object, giving it the path to `WorkerSocket.ts` and also sends a message to the worker with the `settingsConfig` stating to initialise the WebSocket.

- `workerOnMessageHandler` is callback function that is responsible for handling the messages sent from the worker to UI. Here, we save the data in redux state.

## WorkerSocket.ts
`path: ./src/worker_socket\WorkerSocket.ts` <br/><br/>
- Mainly handles the WebSocket code for connecting, disconnecting, connection_error, pinging, receiving messages and buffering them, keep in mind the code in this file runs in the background.

- Also contains `onmessage` which is a listener that's responsible for receiving the communication from `App.ts` (UI thread), to start and terminate the websocket.

## MainThreadCallbacks.ts
`path: ./src/worker_socket/MainThreadCallbacks.ts`
- In this file, convinently named Main Thread Callbacks because it has methods that call `postMessage` which is the way to communicate back with the UI thread in order to update the redux state.

- Messages are buffered on the websocket endpoint then flushed to be processed here inside `updateMainThreadCallback` before being send to the UI thread. 

### But because we have different events, the methods to handle each of them is in a separate file inside `path: ./src/worker_socket/event_handlers`.

Mainly the methods inside each file are responsible for reformating their respective data into the form that is defined in [ReduxDataStructures.md](./ReduxDataStructures.md).


### And that’s how we get streaming data through WebSocket and WebWorker without blocking the main thread and slowing down the application. <br/><br/>