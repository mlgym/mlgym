from gunicorn.app.base import BaseApplication
from flask import Flask
import os
import urllib.parse


class StandaloneApplication(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_ml_board(ml_board_host: str, ml_board_port: str, rest_endpoint: str, ws_endpoint: str, run_id: str):
    static_folder_path = os.path.abspath(os.path.join(__file__, "../../../frontend/dashboard/build"))
    print(f"Delivering static react files from {static_folder_path}")
    app = Flask(__name__, static_folder=static_folder_path, static_url_path='/')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # app.run(host=f"{ml_board_host}", port=ml_board_port)

    options = {
        'bind': f"{ml_board_host}:{ml_board_port}",
        'workers': 1
    }
    rest_endpoint_encoded = urllib.parse.quote(rest_endpoint)
    ws_endpoint_encoded = urllib.parse.quote(ws_endpoint)
    run_id_encoded = urllib.parse.quote(run_id)
    url = f"http://{ml_board_host}:{ml_board_port}?rest_endpoint={rest_endpoint_encoded}&ws_endpoint={ws_endpoint_encoded}&run_id={run_id_encoded}"
    print(f"====> ACCESS MLBOARD VIA {url}")
    StandaloneApplication(app, options).run()
