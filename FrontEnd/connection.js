
// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:3000');

// Connection opened
socket.addEventListener('open', function (event) {
    console.log('Connected to WS Server')
});

// Listen for messages
socket.addEventListener('message', function (event) {
  //  console.log('Message from server ', event.data);
  //   const data = event.data;
});

socket.onmessage = function(event){
  console.log(event.data);
  const data = event.data;
  return data
}

function startWebSocket(data){
  $("#messages").append(data);
}
