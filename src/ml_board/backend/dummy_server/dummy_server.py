####################################################################################################
# imports (how to state the obvious 101 x'D)
import json
import sys
from collections import defaultdict
from typing import List

from flask import Flask, copy_current_request_context, render_template, request
from flask_socketio import SocketIO, disconnect, emit, join_room, rooms


####################################################################################################
# Flask HTTP Server
def create_flask_server() -> Flask:
    # create Flask server
    _app: Flask = Flask(__name__, template_folder="template")
    _app.secret_key = 'secret!'

    # set routes with their respective callbacks
    _app.add_url_rule('/', view_func=_index)
    # _app.add_url_rule('/api/status', view_func=_api_status)

    return _app


def _index() -> str:
    # return render_template('index.html', async_mode=ws._socketio.async_mode)
    return "Index Page"

# def _api_status() -> dict:
#     client_sids = ws.client_sids
#     room_key_to_sid = defaultdict(list)
#     for client_sid in client_sids:
#         room_keys = rooms(client_sid, "/")
#         for room_key in room_keys:
#             room_key_to_sid[room_key].append(client_sid)
#     return {"clients": client_sids, "rooms": room_key_to_sid}

# TODO: RESTful APIs could be added here!


####################################################################################################
# Web Socket


class WebSocketWrapper:
    def __init__(self, flask_app: Flask, host: str, port: int, async_mode: str, message_delay: int, log_file_path: str, line_count: int, cors_ports: list[int]):
        # array of connected client session ids
        self._client_sids = []
        self._message_delay = message_delay

        # create the websocket
        self._socketio = SocketIO(flask_app,
                                  async_mode=async_mode,
                                  cors_allowed_origins=[url for port in cors_ports for url in (f"http://localhost:{port}", f"http://127.0.0.1:{port}")])
        # initialize callbacks
        self._socketio.on_event("connect", self._on_connect)
        self._socketio.on_event("disconnect", self._on_disconnect)
        self._socketio.on_event("ping", self._on_ping)
        self._socketio.on_event("join", self._on_join)
        self._socketio.on_event("leave", self._on_leave)
        # load the log file
        self._load_log_file(log_file_path, line_count)
        # NOTE: starting the server at the very end as the call to run is blocking!
        self._socketio.run(flask_app, host=host, port=port, debug=False)

    def _load_log_file(self, log_file_path: str, how_many_lines: int):
        with open(log_file_path, encoding="utf-8") as fp:
            self._log_list = fp.readlines()
        self._how_many_lines = how_many_lines if how_many_lines != -1 else len(self._log_list)

    def _emit_server_log_message(self, data):
        print(data)
        emit("server_log_message", data)

    def _on_ping(self):
        emit('pong')

    def _on_connect(self):
        self._emit_server_log_message(f"Client with SID {request.sid} connnected.")

    def _on_disconnect(self):
        print('Client disconnected', request.sid)
        self._client_sids.remove(request.sid)

    def _on_join(self, data):
        @copy_current_request_context
        def _send_event_history_to_client():
            for i, msg in enumerate(self._log_list):
                if i == self._how_many_lines:
                    print("DONE!")
                    break
                self._socketio.emit('mlgym_event', json.loads(msg))
                self._socketio.sleep(self._message_delay)

        # save the sids of the new client
        self._client_sids.append(request.sid)
        # TODO: ASK WHY isn't client id and sid the same?
        client_id = data['client_id'] if 'client_id' in data else "<unknown>"
        # join the rooms we want to subcribe to
        for room in data['rooms']:
            join_room(room)
        # TODO: ASK WHY the client_sid is added to the rooms?
        self._emit_server_log_message(f"Client {client_id} joined rooms: {rooms()}")

        # send the history of log messages to the client
        if "mlgym_event_subscribers" in data['rooms']:
            self._socketio.start_background_task(_send_event_history_to_client)

    def _on_leave(self):
        self._client_sids.remove(request.sid)
        # old TODO leave all rooms (ASK HOW?)
        # leave_room(message['room'])
        self._emit_server_log_message("You are now disconnected.")
        disconnect()

    # @property
    # def client_sids(self) -> List[str]:
    #     return self._client_sids

####################################################################################################
# main (starting point)


params = ["path", "line_count", "port", "delay", "cors_ports"]
# sys.argv EXAMPLE: path=event_storage.log line_count=500 port=7000 delay=0.1 cors_ports=3000,7000,8080
if __name__ == '__main__':

    sys.argv.pop(0)
    args = dict([arg.split('=') for arg in sys.argv])
    print(f"{args}\n{'Valid parameters ✔' if all(arg in params for arg in args) else 'Invalid parameters ✗'}")
    
    if params[0] not in args:
        print(f"missing [path], must be provided!!!")
        sys.exit(0)

    try:
        # run the Server
        WebSocketWrapper(
            flask_app=create_flask_server(),
            host="localhost",
            port=args.get('port', 7000),
            async_mode=None,
            message_delay=float(args.get('delay', 0.1)),  # in seconds
            log_file_path=args['path'],
            line_count=int(args.get('line_count', -1)),
            cors_ports= args.get('cors_ports', "3000,7000,8080").split(',')
        )
    except Exception as e:
        print(">>>:", e, str(e))
