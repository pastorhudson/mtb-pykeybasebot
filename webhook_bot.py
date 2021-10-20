import json
from flask import Flask
from pathlib import Path
import subprocess
import os

app = Flask(__name__)


@app.route("/")
def hello_world():
    send_msg("Hello worldddd")
    return "<p>Hello, World!</p>"


def send_msg(msg):
    you = 'pastorhudson'
    them = os.environ.get('KEYBASE_BOTNAME')
    payload = {"method": "send", "params": {
        "options": {"channel": {"name": f"{you},{them}"}, "message": {"body": msg}}}}

    marvinpath = Path(f'./{os.environ.get("KEYBASE_BOTNAME")}n')
    subprocess.run(args=['keybase', '--home', marvinpath.resolve(), 'chat', 'api', '-m', json.dumps(payload)] )


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
