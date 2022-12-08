import socketio
from typing import Dict, List


class ClientFactory:

    @staticmethod
    def get_buffered_client(client_id: str, host: str, port: int, disconnect_buffer_size: int, rooms: List[str]):
        sio_client = socketio.Client()
        bc = BufferedClient(client_id=client_id,
                            host=host,
                            port=port,
                            disconnect_buffer_size=disconnect_buffer_size,
                            sio_client=sio_client,
                            rooms=rooms)
        bc.connect()
        return bc


class BufferedClient:

    def __init__(self, client_id: str, host: str, port: int, disconnect_buffer_size: int, sio_client: socketio.Client, rooms: List[str]):
        self._client_id = client_id
        self._host = host
        self._port = port
        self._disconnect_buffer_size = disconnect_buffer_size
        self._sio_client = sio_client
        self.rooms = rooms

    @staticmethod
    def _register_callback_funs(sio_client: socketio.Client):
        # on message event
        sio_client.on("server_log_message", BufferedClient.on_server_log_message)
        sio_client.on("mlgym_event", BufferedClient.on_mlgym_event_message)

    def connect(self):
        self._sio_client.connect(f"{self._host}:{self._port}", wait=True, wait_timeout=20)
        BufferedClient._register_callback_funs(self._sio_client)
        self.emit("join", {"client_id": self._client_id, "rooms": [*self.rooms, self._client_id]})

    def leave(self):
        self.emit("leave", None)

    def on_server_log_message(data: Dict):
        print(data)

    def on_mlgym_event_message(data: Dict):
        print(data)
        # with open("log.txt", 'a') as fp:
        #     fp.write(json.dumps(data) + "\n")

    def emit(self, message_key: str,  message: Dict):
        self._sio_client.emit(message_key, message)
        # print(f"Sent message {message_key}: {message}")

