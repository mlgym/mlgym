import os
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from ml_gym.backend.messaging.event_storage import EventStorageIF, EventStorageFactory
from typing import Any, List, Dict
from collections import defaultdict
from engineio.payload import Payload
from pathlib import Path

Payload.max_decode_packets = 10000


class EventSubscriberIF:

    def callback(self):
        raise NotImplementedError


class WebSocketServer:

    def __init__(self, port: int, async_mode: str, app: Flask, top_level_logging_path: str):
        self._port = port
        self._socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=["http://localhost:3000", "http://localhost:7000"],
                                  max_http_buffer_size=100000000000)
        self._client_sids = []
        self._top_level_logging_path = top_level_logging_path
        self.mlgym_event_logging_path = os.path.join(self._top_level_logging_path, "logs")
        self._room_id_to_event_storage: Dict[str, EventStorageIF] = {
            "mlgym_event_subscribers": EventStorageFactory.get_disc_event_storage(logging_path=self.mlgym_event_logging_path)
        }
        self._init_call_backs()

    def emit_server_log_message(self, data):
        emit("server_log_message", data)

    @property
    def client_sids(self) -> List[str]:
        return self._client_sids

    def _send_event_history_to_client(self, client_id: str, room_id: str):
        event_storage = self._room_id_to_event_storage[room_id]
        event_storage_ids = event_storage.event_storage_ids
        if event_storage_ids:
            event_storage_id = event_storage_ids[-1]
            print(f"=== WEBSOCKET SERVER LOG ===: Sending {event_storage.length(event_storage_id)} old messages from room {room_id} to client {client_id}")
            for event_id, event in event_storage.iter_generator(event_storage_id):  # TODO make grid search id selectable
                emit('mlgym_event', {'event_id': event_id, 'data': event}, room=client_id)

    def _init_call_backs(self):

        @self._socketio.on("join")
        def on_join(data):
            client_sid = request.sid
            self._client_sids.append(client_sid)
            if 'client_id' in data:
                client_id = data['client_id']
            else:
                client_id = "<unknown>"
            rooms_to_join = data['rooms']
            for room in rooms_to_join:
                if room not in self._room_id_to_event_storage:
                    self._room_id_to_event_storage[room] = EventStorageFactory.get_disc_event_storage(logging_path=f"/home/mluebberin/repositories/github/private_workspace/mlgym/event_storage/{room}")
                join_room(room)
            print(f"Client {client_id} joined rooms: {rooms()}")
            self.emit_server_log_message(f"Client {client_id} joined rooms: {rooms()}")
            for room in rooms_to_join:
                self._send_event_history_to_client(client_sid, room)

        @self._socketio.on("leave")
        def on_leave():
            self._client_sids.remove(request.sid)
            # TODO  leave all rooms
            # leave_room(message['room'])
            self.emit_server_log_message("You are now disconnected.")
            disconnect()

        @self._socketio.on("mlgym_event")
        def on_mlgym_event(data):
            grid_search_id = data["payload"]["grid_search_id"]
            if data["event_type"] in set(["experiment_status", "job_status", "experiment_config", "evaluation_result"]):
                print("mlgym_event: " + str(data))
                event_id = self._room_id_to_event_storage["mlgym_event_subscribers"].add_event(grid_search_id, data)
                emit('mlgym_event', {'event_id': event_id, 'data': data}, to="mlgym_event_subscribers")
            elif data["event_type"] == "checkpoint":
                self.save_checkpoint(checkpoint=data["payload"], path=self.mlgym_event_logging_path)
            else:
                print(f"Unsupported event_type {data['event_type']}")

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

        @self._socketio.on("ping")
        def on_ping():
            emit('pong')

        @self._socketio.on("client_connected")
        def on_client_connected():
            print(f"Client with SID {request.sid} connnected.")
            self.emit_server_log_message(f"Client with SID {request.sid} connnected.")

        @self._socketio.on("client_disconnected")
        def on_client_disconnected():
            print('Client disconnected', request.sid)
            self._client_sids.remove(request.sid)

    def run(self, app: Flask):
        self._socketio.run(app)

    def save_checkpoint(self, checkpoint: Dict[str, Any], path: str):
        grid_search_id = checkpoint["grid_search_id"]
        experiment_id = checkpoint["experiment_id"]
        checkpoint_id = checkpoint["checkpoint_id"]

        full_path = os.path.join(path, grid_search_id, str(experiment_id), str(checkpoint_id))
        os.makedirs(full_path, exist_ok=True)
        for key, stream in checkpoint["checkpoint_streams"].items():
            checkpoint_element_path = os.path.join(full_path, key + ".bin")
            if os.path.exists(checkpoint_element_path):
                os.remove(checkpoint_element_path)
                parent_dir = Path(checkpoint_element_path).parent
                if not any(Path(parent_dir).iterdir()):  # if the directory is empty we can also just remove the folder
                    os.rmdir(parent_dir)
            else:
                with open(checkpoint_element_path, "wb") as fd:
                    fd.write(stream)


if __name__ == '__main__':
    top_level_logging_path = "event_storage/"
    app = Flask(__name__, template_folder="template")
    app.config['SECRET_KEY'] = 'secret!'

    # thread = socketio.start_background_task(background_thread, )
    port = 5000
    async_mode = None

    ws = WebSocketServer(port=port, async_mode=async_mode, app=app, top_level_logging_path=top_level_logging_path)

    @app.route('/')
    def index():
        return render_template('index.html', async_mode=ws._socketio.async_mode)

    @app.route('/status')
    def status():
        return render_template('status.html', async_mode=ws._socketio.async_mode)

    @app.route('/api/status')
    def api_status():
        client_sids = ws.client_sids
        room_key_to_sid = defaultdict(list)
        for client_sid in client_sids:
            room_keys = rooms(client_sid, "/")
            for room_key in room_keys:
                room_key_to_sid[room_key].append(client_sid)

        return {"clients": client_sids, "rooms": room_key_to_sid}
    print(ws._socketio.async_mode)
    ws.run(app)
