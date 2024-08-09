import asyncio
import logging
from collections import defaultdict
from datetime import datetime

import pytz
from flask import jsonify, render_template
from werkzeug.exceptions import BadRequest, HTTPException
from botcommands.youtube_dlp import get_mp4
from flask import send_file
from yt_dlp.utils import DownloadError
from flask import Flask, request
from crud import s
from models import MessageQueue, ALGORITHM, JWT_SECRET_KEY, User, JWT_REFRESH_SECRET_KEY, Till
from jose import jwt
from pydantic import ValidationError
from pydantic import BaseModel
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import escape

app = Flask(__name__, template_folder='/app/www')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
logging.basicConfig(level=logging.DEBUG)


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
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON data"}), 400
    message = escape(data.get('message'))
    # destination = escape(data.get('destination'))
    sender = escape(data.get('sender'))
    token = escape(data.get("token"))
    client_ip = escape(request.remote_addr)
    try:
        user, conversation_id = asyncio.run(get_user(token))
    except HTTPException as e:
        logging.info(e)
        return jsonify({"error": "Could Not Validate Credentials"}), 403

    if not message or not token:
        return jsonify({"error": "Missing data"}), 400

    session = s
    new_message = MessageQueue(message=message, destination=conversation_id, sender=sender, ip=client_ip, user=user)
    session.add(new_message)
    session.commit()
    return {"message": "Message added successfully."}, 201


@app.route('/refresh', methods=['POST'])
def auth_refresh():
    logging.info("refresh token")
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON data"}), 400
    token = escape(data.get("token"))

    client_ip = escape(request.remote_addr)
    logging.info(f"Client IP: {client_ip} attempting to refresh token")
    try:
        user, conversation_id = asyncio.run(check_refresh(token))
    except HTTPException as e:
        logging.info(e)
        return jsonify({"error": str(e)}), 403
    if not token:
        return jsonify({"error": "Missing data"}), 400

    return jsonify({"token": user.create_access_token(conversation_id=conversation_id),
                    "refresh_token": user.create_refresh_token(conversation_id=conversation_id)}), 200


@app.route('/till', methods=['GET'])
def get_till():
    token = request.args.get("token")
    logging.info(f"token: {token} THIS IS A TILL REQUEST")
    if not token:
        return jsonify({"error": "Missing token"}), 400
    try:
        client_ip = escape(request.remote_addr)
        logging.info(f"Client IP: {client_ip}")
        user, conversation_id = asyncio.run(get_user(token))
    except HTTPException as e:
        logging.info(e)
        return jsonify({"error": "Could Not Validate Credentials"}), 403

    team_tills = defaultdict(list)

    team_tills = defaultdict(list)

    for team in user.teams:
        for till in team.tills:
            days, hours, minutes = calculate_time_difference(till.event)
            till.days = days
            till.hours = hours
            till.minutes = minutes
            team_tills[team.name].append(till)
    return render_template('tills.html', team_tills=team_tills, user=user)


def calculate_time_difference(event_time):
    # Make the current time timezone-aware with the same timezone as event_time
    now = datetime.now(pytz.UTC)
    time_difference = event_time - now
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return days, hours, minutes

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    user: str = None
    conversation_id: str = None
    exp: int = None


class RefreshTokenPayload(BaseModel):
    user: str = None
    conversation_id: str = None
    exp: int = None
    refresh_token: bool = False


async def get_user(token: str):
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException("Token Expired")

    except (jwt.JWTError, ValidationError):
        raise HTTPException("Could not validate credentials")

    user = s.query(User).filter(User.username == token_data.user).first()
    conversation_id = token_data.conversation_id

    if user is None:
        raise HTTPException("Could not find user")

    return user, conversation_id


async def check_refresh(token: str):
    try:
        payload = jwt.decode(
            token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        logging.info(payload)
        token_data = RefreshTokenPayload(**payload)
        logging.info(datetime.fromtimestamp(token_data.exp))
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException("Token Expired")

    except (jwt.JWTError, ValidationError):
        raise HTTPException("Could not validate credentials")
    logging.info("processed token")
    user = s.query(User).filter(User.username == token_data.user).first()
    conversation_id = token_data.conversation_id
    logging.info("got user and convo")
    if user is None:
        raise HTTPException("Could not find user")

    return user, conversation_id

# if __name__ == '__main__':
#     # Bind to PORT if defined, otherwise default to 5000.
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='127.0.0.1', port=port)
