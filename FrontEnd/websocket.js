const express = require('express')
const app = express()
const server = require('http').createServer(app);
const WebSocket = require('ws');
const fs = require('fs');
const wss = new WebSocket.Server({ server:server });
const JSONStream = require('JSONStream');
const es = require('event-stream');

const websocketStream = require("websocket-stream");

var getStream = function () {
    var jsonData = 'public/example.json',
        stream = fs.createReadStream(jsonData, { encoding: 'utf8' }),
        parser = JSONStream.parse('*');
    return stream.pipe(parser);
};
//var json = {"event_id": 0, "data": {"event_type": "evaluation_result", "creation_ts": 1650878091595520, "payload": {"job_id": 0, "job_type": 1, "status": "INIT", "experiment_id": "2022-04-25--11-14-51/conv_net/0", "starting_time": -1, "finishing_time": -1, "device": "", "error": null, "stacktrace": null}}}

wss.on('connection', function connection(ws) {
  console.log('A new client Connected!');
  ws.send('Welcome New Client!\n');
  ws.send('\n');
  getStream()
      .pipe(es.mapSync(function (data) {
          ws.send(JSON.stringify(data) + "\n");
      }));

});

app.get('/', (req, res) => res.send('Hello World!'))

server.listen(3000, () => console.log(`Listening on port :3000`))
