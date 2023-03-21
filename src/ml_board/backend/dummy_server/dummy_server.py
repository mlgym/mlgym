####################################################################################################
# imports
import json
import sys
from collections import defaultdict
from typing import List

from flask import Flask, copy_current_request_context, render_template, request
from flask_socketio import SocketIO, disconnect, emit, join_room, rooms

####################################################################################################
# TODO: ASK Max what's that for?
# class EventSubscriberIF:
#     def callback(self):
#         raise NotImplementedError


####################################################################################################
# Flask HTTP Server
def CreateFlaskServer() -> Flask:
    # create Flask server
    _app: Flask = Flask(__name__, template_folder="template")
    _app.secret_key = 'secret!'

    # set routes with their respective callbacks
    _app.add_url_rule('/', view_func=_index)
    # _app.add_url_rule('/status', view_func=_status)
    # _app.add_url_rule('/api/status', view_func=_api_status)

    return _app


def _index() -> str:
    # return render_template('index.html', async_mode=ws._socketio.async_mode)
    return "Index Page"


# def _status() -> str:
#     return render_template('status.html', async_mode=ws._socketio.async_mode)


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
    def __init__(self, flask_app: Flask, host: str, port: int, async_mode: str, message_delay: int, log_file_path: str, how_many_lines: int):
        # array of connected client session ids
        self._client_sids = []
        self._message_delay = message_delay

        # create the websocket
        self._socketio = SocketIO(flask_app,
                                  async_mode=async_mode,
                                  cors_allowed_origins=["http://localhost:3000", "http://localhost:7000", "http://localhost:8080",
                                                        "http://127.0.0.1:3000", "http://127.0.0.1:7000", "http://127.0.0.1:8080"])
        # initialize callbacks
        self._socketio.on_event("connect", self._on_connect)
        self._socketio.on_event("disconnect", self._on_disconnect)
        self._socketio.on_event("ping", self._on_ping)
        self._socketio.on_event("join", self._on_join)
        self._socketio.on_event("leave", self._on_leave)
        # load the log file
        self._load_log_file(log_file_path, how_many_lines)
        # NOTE: starting the server at the very end as the call to run is blocking!
        self._socketio.run(flask_app, host=host, port=port, debug=False)

    def _load_log_file(self, log_file_path: str, how_many_lines: int):
        with open(log_file_path, encoding="utf-8") as fp:
            self._log_list = fp.readlines()
        self._how_many_lines = how_many_lines if how_many_lines != -1 else len(self._log_list)

    # def _emit_server_log_message(self, data):
    #     emit("server_log_message", data)

    def _on_ping(self):
        emit('pong')

    def _on_connect(self):
        print(f"Client with SID {request.sid} connnected.")
        # self._emit_server_log_message(f"Client with SID {request.sid} connnected.")

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
        print(f"Client {client_id} joined rooms: {rooms()}")
        # self._emit_server_log_message(f"Client {client_id} joined rooms: {rooms()}")

        # send the history of log messages to the client
        if "mlgym_event_subscribers" in data['rooms']:
            self._socketio.start_background_task(_send_event_history_to_client)

    def _on_leave(self):
        self._client_sids.remove(request.sid)
        # TODO  leave all rooms
        # leave_room(message['room'])
        # self._emit_server_log_message("You are now disconnected.")
        disconnect()

    # @property
    # def client_sids(self) -> List[str]:
    #     return self._client_sids

####################################################################################################
# main (starting point)


if __name__ == '__main__':

    # make sure the user input all arg_keys
    input_len = len(sys.argv)
    arg_keys = ['program_name', 'log_file_path', 'how_many_lines']
    if input_len != len(arg_keys):
        print(f"missing args: {arg_keys[input_len:]}")
        print("how_many_lines could be -1 for the entire file!")
        sys.exit(0)
    argvs = dict(zip(arg_keys, sys.argv))

    try:
        # run the Server
        WebSocketWrapper(
            flask_app=CreateFlaskServer(),
            host="localhost",
            port=7000,
            async_mode=None,
            message_delay=0.1,  # in seconds
            log_file_path=argvs['log_file_path'],
            how_many_lines=int(argvs['how_many_lines']),
        )
    except Exception as e:
        print(">>>:", e, str(e))
