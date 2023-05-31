import os
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from ml_board.backend.messaging.event_storage import EventStorageIF, EventStorageFactory
from typing import Any, List, Dict
from engineio.payload import Payload
from pathlib import Path
from ml_board.backend.websocket_api.checkpoint_cache import CheckpointCache, CheckpointEntity, CheckpointEntityTransferStatus
from ml_gym.error_handling.exception import CheckpointEntityError

Payload.max_decode_packets = 1e9


class EventSubscriberIF:
    def callback(self):
        raise NotImplementedError


class WebSocketServer:
    """
    Websocket Server class

    Creates websocket Object with socket connection for given host and port.
    :params:
            host (str): Host Srver IP
            port (int): port number on which websocket will run
            async_mode (str):  Sync mode
            app (Flask Obj): Flask server object
            top_level_logging_path (str): path of folder where logs will be stored
            cors_allowed_origins (List[str]): the IPs who will be allowed to communicate with the websocket.

    """

    def __init__(self, host: str, port: int, async_mode: str, app: Flask, top_level_logging_path: str, cors_allowed_origins: List[str]):
        # parameters for the run function
        self._run = { "port": port, "host": host, "app": app }
        # create the websocket
        self._socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=cors_allowed_origins, max_http_buffer_size=1e11)
        # array of connected client session ids
        self._client_sids = []
        # the path to the event_storage directory
        self._top_level_logging_path = top_level_logging_path
        # dictionary between rooms and event storages
        self._room_id_to_event_storage: Dict[str, EventStorageIF] = {
            # "mlgym_event_subscribers": EventStorageFactory.get_disc_event_storage(parent_dir=self.mlgym_event_logging_path)
        }
        # initialize callbacks
        self._init_call_backs()
        # creating a checkpoint cache
        self._checkpoint_cache = CheckpointCache()

    # NOTE: the call to this function is blocking!
    def run(self):
        self._socketio.run(
            self._run["app"], host=self._run["host"], port=self._run["port"])

    @property
    def client_sids(self) -> List[str]:
        return self._client_sids

####################################################################################################
# callbacks 
    def _init_call_backs(self):
        self._socketio.on_event("client_connected", self._on_client_connected)
        self._socketio.on_event("client_disconnected", self._on_client_disconnected)
        self._socketio.on_event("ping", self._on_ping)
        self._socketio.on_event("join", self._on_join)
        self._socketio.on_event("leave", self._on_leave)
        self._socketio.on_event("mlgym_event", self._on_mlgym_event)

    def _on_join(self, data):
        client_sid = request.sid
        self._client_sids.append(client_sid)
        client_id = data["client_id"] if "client_id" in data else "<unknown>"
        rooms_to_join = data["rooms"]
        for room in rooms_to_join:
            if room not in self._room_id_to_event_storage:
                self._room_id_to_event_storage[room] = EventStorageFactory.get_disc_event_storage(
                    parent_dir=self._top_level_logging_path, event_storage_id=room
                )
            join_room(room)
        self._emit_server_log_message(f"Client {client_id} joined rooms: {rooms()}")
        for room in rooms_to_join:
            self._send_event_history_to_client(client_sid, room)

    def _on_leave(self):
        self._client_sids.remove(request.sid)
        # TODO  leave all rooms
        # leave_room(message['room'])
        self._emit_server_log_message("You are now disconnected.")
        disconnect()

    def _on_mlgym_event(self, data):
        grid_search_id = data["payload"]["grid_search_id"]
        if data["event_type"] in set(["experiment_status", "job_status", "experiment_config", "evaluation_result"]):
            print("mlgym_event: " + str(data))
            if grid_search_id not in self._room_id_to_event_storage:
                self._room_id_to_event_storage[grid_search_id] = EventStorageFactory.get_disc_event_storage(
                    parent_dir=self._top_level_logging_path, event_storage_id=grid_search_id
                )
            event_id = self._room_id_to_event_storage[grid_search_id].add_event(data)
            emit('mlgym_event', {'event_id': event_id, 'data': data}, to=grid_search_id)
        else:
            print(f"Unsupported event_type {data['event_type']}")

    def _on_ping(self):
        emit("pong")

    def _on_client_connected(self):
        self._emit_server_log_message(
            f"Client with SID {request.sid} connnected.")

    def _on_client_disconnected(self):
        print("Client disconnected", request.sid)
        self._client_sids.remove(request.sid)
        
    # @socketio.event
    # def disconnect_request():
    #     @copy_current_request_context
    #     def can_disconnect():
    #         disconnect()

    #     session['receive_count'] = session.get('receive_count', 0) + 1
    #     # for this emit we use a callback function
    #     # when the callback function is invoked we know that the message has been
    #     # received and it is safe to disconnect
    #     emit('my_response',
    #          {'data': 'Disconnected!', 'count': session['receive_count']},
    #          callback=can_disconnect)-


####################################################################################################
# private helper functions

    def _emit_server_log_message(self, data):
        print(data)
        emit("server_log_message", data)

    def _send_event_history_to_client(self, client_id: str, room_id: str):
        batch = []
        event_storage = self._room_id_to_event_storage[room_id]
        print(f"=== WEBSOCKET SERVER LOG ===: Sending {event_storage.length()} old messages from room {room_id} to client {client_id}")
        for event_id, event in event_storage.iter_generator():  # TODO make grid search id selectable
            batch.append({"event_id": event_id, "data": event})
        if len(batch) > 0:
            emit("mlgym_event", {"event_id": "batched_events", "data": batch}, room=client_id)
        # emit('mlgym_event', {'event_id': event_id, 'data': event}, room=client_id)

####################################################################################################
# Flask HTTP Server
def create_flask_server() -> Flask:
    # create Flask server
    _app: Flask = Flask(__name__, template_folder="template")
    _app.secret_key = 'secret!'
    return _app

####################################################################################################
# main

if __name__ == '__main__':

    WebSocketServer(
        host="127.0.0.1",
        port=5002,
        async_mode=None,
        app=create_flask_server(),
        top_level_logging_path="/event_storage",
        cors_allowed_origins=["http://localhost:5001", "http://localhost:3000", "http://127.0.0.1:3000"],
    ).run()
