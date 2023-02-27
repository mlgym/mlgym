# Web-Workers

In this project, we have used web-workers which gives us the advantage of working on the tasks seperately from the main UI thread.<br/>

Initialising the WebSocket in the main thread would slow down the website and make it feel laggy since constantly it would be handling the server data that is pushed in through the WebSocket.<br/>

One way to do this efficiently is by initialising the WebSocket inside a WebWorker. WebWorker does not execute in the main thread instead it will be executed in a separate thread in parallel to the main thread which handles the rendering and handling of user actions.

To get a detailed understanding of these two Web API’s you can go through the following:<br/><br/>

WebSockets — https://blog.logrocket.com/websockets-tutorial-how-to-go-real-time-with-node-and-react-8e4693fbf843/ <br/><br/>

WebWorkers:<br/>
Video — https://youtu.be/Gcp7triXFjg <br/>
Blog — https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API <br/><br/>

WebSockets inside WebWorkers — https://jpsam7.medium.com/react-app-with-websocket-implemented-inside-webworker-aba6374e54f0 <br/><br/>

We will be getting streamable data from the our endpoint (can be localhost or a custom url).

The code to achieve this is split across 4 files.
1. AppNew.js
2. DedicatedWorkerClass.js
3. SocketClass.js
4. worker.js

## AppNew.js
`path: ./src/app/AppNew.js` <br/><br/>
- Here, from the `componentDidMount` lifecycle method we trigger the `createWorker` function, which will create an instance of `DedicatedWorkerClass` and also sends a message to the worker "`START`" stating to initialise the WebSocket. `DedicatedWorkerClass` is a wrapper around the actual worker API.

- Inside `createWorker` we give the constructor of `DedicatedWorkerClass` the function `workerOnMessageHandler`.
This method is responsible for handling the messages sent from the worker to UI and do appropriate actions on the data returned. Here, we will be saving the data in redux state.

## DedicatedWorkerClass.js
`path: ./src/webworkers/DedicatedWorkerClass.js` <br/><br/>
- Inside the constructor of DedicatedWorkerClass we initialise the worker object. The name of the worker file doesn’t necessarily have to be `worker.js` you can name it as per your use case. 

## worker.js
`path: ./src/webworkers/worker.js`
- In this file, the `onmessage` method will set the `onmessage` handler of worker object. This event handler will be triggered whenever the main thread sends any message using the `postMessage` API (eg: I have sent redux data from `AppNew.js` to update it with new data from websocket). Before we transfer the control to `doAction` method we can validate the request data using `validateEventData` to make sure it follows the data communication pattern we have defined (For now I have sent true by default).

- We send the function `workerOnMessageCallback` as one of the parameters for the SocketClass. This function will be used by the Socket to post the data it is retrieving.

- We are following this pattern wherein we are sending a function to the Socket is that the `postMessage` function will not be available outside the worker scope.

- So when we try to access `postMessage` from inside SocketClass it will be `undefined`. Hence we pass a function callback which will be used to send the message from socket to worker and hence to the UI.

## SocketClass.js
`path: ./src/websocket/SocketClass.js`
- The init function of `SocketClass` in called from `worker.js` which initialises the webSocket with the streaming data URL endpoint.

- Once the WebSocket connection is opened, we subscribe to the `mlgym_event` of the websocket connection to the server.

- After we have subscribed to the data we will start receiving information from the back-end continuously. We handle these messages using `handleEventMessage` handler. It processes the data as required by the UI. (For example, `EVALUATION_RESULT` are handled by an event handler: `handleEvaluationResultData`)

- We send this info to the main thread using the `dataCallback` function which is the `workerOnMessageCallback` function in `worker.js` which uses the `postMessage` API of WebWorker to send the data back to the main thread (here, the data goes back to `workerOnMessageHandler` in `AppNew.js` via `onMessage` method from `DedicatedWorkerClass.js`).

### And that’s how we get streaming data through WebSocket and WebWorker without blocking the main thread and slowing down the application. <br/><br/>