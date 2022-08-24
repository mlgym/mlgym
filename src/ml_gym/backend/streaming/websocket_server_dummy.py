from flask import Flask, render_template, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, rooms, disconnect
from typing import List
from collections import defaultdict


class EventSubscriberIF:

    def callback(self):
        raise NotImplementedError


class WebSocketServer:

    def __init__(self, host: str, port: int, message_delay: int, log_file_path: str, async_mode: str, app: Flask):
        self._host = host
        self._port = port
        self._message_delay = message_delay
        self._socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=["http://localhost:3000", "http://localhost:7000"])
        self._client_sids = []
        self._init_call_backs()

        # load the log file
        with open(log_file_path, encoding="utf-8") as fp:
            self.log_list = fp.readlines()

    def run(self, app: Flask):
        self._socketio.run(app, host=self._host, port=self._port)

    def emit_server_log_message(self, data):
        emit("server_log_message", data)

    @property
    def client_sids(self) -> List[str]:
        return self._client_sids

    def _init_call_backs(self):

        @self._socketio.on("join")
        def on_join(data):

            @copy_current_request_context
            def _send_event_history_to_client(log_list):
                for msg in log_list:
                    emit('mlgym_event', msg)
                    self._socketio.sleep(self._message_delay)

            # save the sids of the new client
            client_sid = request.sid
            self._client_sids.append(client_sid)
            if 'client_id' in data:
                client_id = data['client_id']
            else:
                client_id = "<unknown>"
            # join the rooms we want to subcribe to
            rooms_to_join = data['rooms']
            for room in rooms_to_join:
                join_room(room)
            print(f"Client {client_id} joined rooms: {rooms()}")
            self.emit_server_log_message(f"Client {client_id} joined rooms: {rooms()}")

            # send the history of log messages to the client
            if "mlgym_event_subscribers" in rooms_to_join:
                self._socketio.start_background_task(lambda: _send_event_history_to_client(self.log_list))

        @self._socketio.on("leave")
        def on_leave():
            self._client_sids.remove(request.sid)
            # TODO  leave all rooms
            # leave_room(message['room'])
            self.emit_server_log_message("You are now disconnected.")
            disconnect()

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


if __name__ == '__main__':
    async_mode = None

    app = Flask(__name__, template_folder="template")
    app.config['SECRET_KEY'] = 'secret!'

    port = 7000
    host = "localhost"
    async_mode = None

    log_file_path = "/home/mluebberin/repositories/github/private_workspace/mlgym/src/ml_gym/backend/streaming/log.txt"

    message_delay = 0.1  # in seconds

    ws = WebSocketServer(host=host, port=port, message_delay=message_delay, log_file_path=log_file_path, async_mode=async_mode, app=app)

    @app.route('/')
    def index():
        return render_template('index.html', async_mode=ws._socketio.async_mode)

    # @app.route('/status')
    # def status():
    #     return render_template('status.html', async_mode=ws._socketio.async_mode)

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
