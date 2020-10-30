import jwt
import os
import urllib.parse
import requests


def get_custom_url(username, room):
    u = f'https://keybase.io/_/api/1.0/user/lookup.json?usernames={username}'
    response = requests.get(u)
    avatar = response.json()['them'][0]['pictures']['primary']['url']

    link = get_jitsi_link(room, avatar, username)
    return link


def get_jitsi_link(room, avatar=None, name=None):
    if not avatar:
        avatar = "https://www.allthetests.com/quiz22/picture/pic_1171831236_1.png"
    if not name:
        name = "Participant"

    payload = \
        {"context": {
            "user": {
                "avatar": avatar,
                "name": name,
                # "email": email,
            }
        },
            "aud": os.environ.get('JITSI_JWT_APP_ID'),
            "iss": os.environ.get('JITSI_JWT_APP_ID'),
            "sub": "meet.jitsi",
            "room": urllib.parse.quote(room)
        }
    encoded_jwt = jwt.encode(payload, os.environ.get('JITSI_JWT_SECRET'), algorithm='HS256')
    url = f"{os.environ.get('JITSI_URL')}/{urllib.parse.quote(room)}?jwt={encoded_jwt.decode('UTF-8')}"

    return url


if __name__ == '__main__':
    # print(get_jitsi_link("My Room"))
    print(get_custom_url("pastorhudson", "my Room"))
