from crud import s
from models import User

def posix(conversation_id, message, sender, token):
    return f"""curl -X POST --location "https://marvn.app/add_message" \
    -H "Content-Type: application/json" \
    -d '{{
            "sender": "{sender}",
            "message": "{message}",
            "destination": "{conversation_id}"
            "token": "{token}"
        }}'"""


def get_powershell(conversation_id, message, sender, token):
    return f"""
    $url = 'https://marvn.app/add_message'
    $headers = @{{
        'Content-Type' = 'application/json'
    }}
    $body = @{{
        'sender' = '{sender}'
        'message' = '{message}'
        'destination' = '{conversation_id}'
        'token' = '{token}'
    }} | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body
    """

def get_json(conversation_id, message, sender, token):
    return f"""POST https://marvn.app/add_message
Content-Type: application/json

{{
  "sender" = "{sender}"
  "message": "{message}",
  "destination": "{conversation_id}",
  "token": "{token}"
}}"""


def get_curl(conversation_id, message, sender, username):
    user = s.query(User).filter(User.username == username).first()
    token = user.create_access_token(conversation_id)
    win_curl = get_powershell(conversation_id, message, sender, token)
    posix_curl = posix(conversation_id, message, sender, token)
    json_curl = get_json(conversation_id, message, sender, token)
    msg = f"""Windoze:```\n{win_curl}\n```\nPosix:\n```\n{posix_curl}\n```\nHTTP POST:```\n{json_curl}\n```"""
    return msg


def extract_message_sender(command, event_body, username):
    body = event_body.replace(command, '', 1).strip()

    if ' -sender ' in body:
        message, sender = map(str.strip, body.split(' -sender ', 1))
    else:
        message = body
        sender = None

    return message, sender


if __name__ == "__main__":
    s = "!notify The server is going down -sender github.com"
    message, sender = extract_message_sender("!notify", s)
    print("Message:", message)
    print("Sender:", sender)

    s = "!notify The server is going down"
    message, sender = extract_message_sender("!notify", s)
    print("Message:", message)
    print("Sender:", sender)

    # print(get_curl("123", "Hello World", "github.com"))