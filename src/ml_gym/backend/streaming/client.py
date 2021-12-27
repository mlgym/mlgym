import socketio
from typing import Dict


class ClientFactory:

    @staticmethod
    def get_buffered_client(client_id: str, host: str, port: int, disconnect_buffer_size: int):
        sio_client = socketio.Client()
        return BufferedClient(client_id=client_id,
                              host=host,
                              port=port,
                              disconnect_buffer_size=disconnect_buffer_size,
                              sio_client=sio_client)


class BufferedClient:

    def __init__(self, client_id: str, host: str, port: int, disconnect_buffer_size: int, sio_client: socketio.Client):
        self._client_id = client_id
        self._host = host
        self._port = port
        self._disconnect_buffer_size = disconnect_buffer_size
        self._sio_client = sio_client
        BufferedClient._register_callback_funs(self._sio_client)

    @staticmethod
    def _register_callback_funs(sio_client: socketio.Client):
        # on message event
        sio_client.on("server_log_message", BufferedClient.on_server_log_message)

    def connect(self):
        self._sio_client.connect(f"{self._host}:{self._port}")
        self.emit("join", {"client_id": self._client_id, "rooms": ["trainers", self._client_id]})

    def leave(self):
        self.emit("leave", None)

    def on_server_log_message(data: Dict):
        print(data)

    def emit(self, message_key: str,  message: Dict):
        self._sio_client.emit(message_key, message)
        print(f"Sent message {message_key}: {message}")


if __name__ == "__main__":
    import time
    host = "http://127.0.0.1"
    port = 5000
    client_id = "worker_1"
    bc = ClientFactory.get_buffered_client(client_id=client_id, host=host, port=port, disconnect_buffer_size=0)
    bc.connect()
    count = 0
    while True:
        bc.emit(message_key="mlgym_event", message=f"Message {count}")
        count += 1
        time.sleep(5)
