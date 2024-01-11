import json
import logging

from flask import jsonify, render_template
import subprocess
import os
from botcommands.youtube_dlp import get_mp4
from flask import send_file
from yt_dlp.utils import DownloadError
from flask import Flask, request
from crud import s
from models import MessageQueue
import socket

app = Flask(__name__, template_folder='/app/www')


@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/add_message', methods=['POST'])
def add_message():
    session = s
    data = request.get_json()
    message = data.get('message')
    destination = data.get('destination')
    sender = data.get('sender')
    client_ip = request.remote_addr
    #
    # try:
    #     sender = socket.getfqdn(client_ip)
    #     logging.info(f'The FQDN for your IP ({client_ip}) is: {sender}')
    # except Exception as e:
    #     sender = client_ip
    #     logging.info('Error obtaining FQDN: {str(e)}')

    new_message = MessageQueue(message=message, destination=destination, sender=sender, ip=client_ip)
    session.add(new_message)
    session.commit()
    return {"message": "Message added successfully."}, 201


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
