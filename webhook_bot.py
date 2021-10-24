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

app = Flask(__name__)


@app.route("/")
def hello_world():
    # send_msg("Hello worldddd")
    return "<p>Hello, World!</p>"


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
    subprocess.run(args=['./keybase', '--home', './webhookbot', 'chat', 'api', '-m', json.dumps(payload)])


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
