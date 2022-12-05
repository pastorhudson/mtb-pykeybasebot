import json
from pprint import pprint
from flask import jsonify
from flask import Flask, request
from pathlib import Path
import subprocess
import os
from botcommands.youtube_dlp import get_meta, get_mp4
from flask import send_file
from yt_dlp.utils import DownloadError
from botcommands.morningreport import get_morningreport

app = Flask(__name__)


@app.route("/")
def hello_world():
    try:
        send_msg("Hello worldddd")
    except Exception as e:
        pass
    return "<p>Hello, World!</p>"

@app.route("/morningreport")
def morning_report():
    try:
        report = get_morningreport('morethanbits')
    except Exception as e:
        report = "ERROR"
        pass
    return f"<p>{report}</p>"


@app.route('/ytv')
def ytv():
    if request.args.get('url'):
        url = request.args.get('url')
        try:
            payload = get_mp4(url)
        # print(payload)
        except DownloadError as e:
            payload = {'Error': str(e)}
            return jsonify(payload)

        try:
            return send_file(payload['file'],
                             attachment_filename='v.mp4')
        except Exception as e:
            return jsonify(payload)
    else:
        return '<p>Wat?</p>'


def send_msg(msg):
    you = 'pastorhudson'
    them = os.environ.get('KEYBASE_BOTNAME')
    payload = {"method": "send", "params": {
        "options": {"channel": {"name": f"{you},{them}"}, "message": {"body": msg}}}}
    print(payload)
    print(['keybase', '--home', './webhookbot', 'chat', 'api', '-m', json.dumps(payload)])
    subprocess.run(args=['env KEYBASE_ALLOW_ROOT=1 & ','./keybase', '--home', './webhookbot', 'chat', 'api', '-m', json.dumps(payload)])


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
