const express = require('express')
const app = express()
const server = require('http').createServer(app);
const WebSocket = require('ws');
fs = require('fs'),
JSONStream = require('JSONStream'),
es = require('event-stream');


const wss = new WebSocket.Server({ server:server });

var getStream = function () {
    var jsonData = 'public/example.json',
        stream = fs.createReadStream(jsonData, { encoding: 'utf8' }),
        parser = JSONStream.parse('*');
    return stream.pipe(parser);
};

getStream()
    .pipe(es.mapSync(function (data) {
        console.log(data);
    }));

wss.on('connection', function connection(ws) {
  console.log('A new client Connected!');
  ws.send('Welcome New Client!');
  ws.send(JSON.stringify(msg));

//to be deleted, clients do no send messages.
  ws.on('message', function incoming(message) {
    console.log('received: %s', message);

    wss.clients.forEach(function each(client) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  });
});

app.get('/', (req, res) => res.send('Hello World!'))

server.listen(3000, () => console.log(`Listening on port :3000`))
