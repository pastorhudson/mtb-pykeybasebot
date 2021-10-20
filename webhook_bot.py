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
    app.run(host='0.0.0.0', port=8080, debug=True)