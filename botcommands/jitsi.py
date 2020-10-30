import jwt
import os
import urllib.parse


def get_jitsi_link(room, avatar=None, name=None, email=None):
    if not avatar:
        avatar = "https://www.allthetests.com/quiz22/picture/pic_1171831236_1.png"
    if not name:
        name = "Participant"
    if not email:
        email = 'email@email.com'

    payload = \
        {"context": {
            "user": {
                "avatar": avatar,
                "name": name,
                "email": email,
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
    print(get_jitsi_link("My Room"))
