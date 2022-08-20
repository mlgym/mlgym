from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from ml_gym.backend.messaging.event_storage import EventStorageIF, EventStorageFactory
from typing import List, Dict
from collections import defaultdict


class EventSubscriberIF:

    def callback(self):
        raise NotImplementedError


class WebSocketServer:

    def __init__(self, port: int, async_mode: str, app: Flask):
        """[summary]

        Args:
            port (int): [description]
            async_mode (str): Set this variable to "threading", "eventlet" or "gevent" to test the
                              different async modes, or leave it set to None for the application to choose
                              the best option based on installed packages.
        """
        self._port = port
        self._socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=["http://localhost:3000", "http://localhost:7000"])
        self._client_sids = []
        self._room_id_to_event_storage: Dict[str, EventStorageIF] = {"mlgym_event_subscribers": EventStorageFactory.get_list_event_storage()}
        self._init_call_backs()

    def emit_server_log_message(self, data):
        emit("server_log_message", data)

    @property
    def client_sids(self) -> List[str]:
        return self._client_sids

    def _send_event_history_to_client(self, client_id: str, room_id: str):
        event_storage = self._room_id_to_event_storage[room_id]
        print(f"=== WEBSOCKET SERVER LOG ===: Sending {len(event_storage)} old messages from room {room_id} to client {client_id}")
        for event_id, event in event_storage:
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
                    self._room_id_to_event_storage[room] = EventStorageFactory.get_list_event_storage()
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
            print("mlgym_event: " + str(data))
            event_id = self._room_id_to_event_storage["mlgym_event_subscribers"].add_event(data)
            emit('mlgym_event', {'event_id': event_id, 'data': data}, to="mlgym_event_subscribers")

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
    #          callback=can_disconnect)

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


if __name__ == '__main__':
    async_mode = None

    app = Flask(__name__, template_folder="template")
    app.config['SECRET_KEY'] = 'secret!'

    # thread = socketio.start_background_task(background_thread, )
    port = 5000
    async_mode = None

    ws = WebSocketServer(port=port, async_mode=async_mode, app=app)

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

    ws.run(app)
