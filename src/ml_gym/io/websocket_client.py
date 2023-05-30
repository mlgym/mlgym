import socketio
from typing import Dict, List


class ClientFactory:
    """
    Websocket Client Factory class.
    """

    @staticmethod
    def get_buffered_client(client_id: str, host: str, port: int, disconnect_buffer_size: int, rooms: List[str]):
        """
        Connect to the Webscoket Buffered Client.
        :params:
            - client_id (str): Client ID wanting to connect to Websocket Server.
            - host (str): Host of Websocket Server.
            - port (int): Port of Websocket Server.
            - disconnect_buffer_size (int): Size of disconnect buffer.
            - rooms (List[str]): List of rooms to join.
        
        :returns:
            BufferedClient Object: Establish connection to websocket server and return back Object.
        """
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
    """
    Buffered Client class.
    """

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
        """
        Webscoket Buffered Client connection function connecting to the Websocket Server.
        """
        self._sio_client.connect(f"{self._host}:{self._port}", wait=True, wait_timeout=20, transports="websocket")
        print(f"Connected to {self._host}:{self._port} with transport protocol {self._sio_client.transport()}")
        BufferedClient._register_callback_funs(self._sio_client)
        self.emit("join", {"client_id": self._client_id, "rooms": [*self.rooms, self._client_id]})

    def disconnect(self):
        self._sio_client.disconnect()

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
