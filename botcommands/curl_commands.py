from crud import s
from models import User


def posix(message, token, sender=None):
    if sender:
        return f"""curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{{"sender": "{sender}", "message": "{message}", "token": "{token}"}}'"""
    else:
        return f"""curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{{"message": "{message}", "token": "{token}"}}'"""


def get_powershell(message, token, sender=None):
    if sender:
        return f"""
$url = 'https://marvn.app/add_message'
$headers = @{{
    'Content-Type' = 'application/json'
}}
$body = @{{
    'sender' = '{sender}'
    'message' = '{message}'
    'token' = '{token}'
}} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body
"""
    else:
        return f"""
$url = 'https://marvn.app/add_message'
$headers = @{{
    'Content-Type' = 'application/json'
}}
$body = @{{
    'message' = '{message}'
    'token' = '{token}'
}} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body
"""


def get_json(message, token, sender=None):
    if sender:
        return \
            f"""POST https://marvn.app/add_message
Content-Type: application/json
    
{{
  "sender" = "{sender}"
  "message": "{message}",
  "token": "{token}"
}}"""
    else:
        return f"""POST https://marvn.app/add_message
Content-Type: application/json

{{
  "message": "{message}",
  "token": "{token}"
}}"""


def get_curl(conversation_id, message, sender, username, channel_name):
    user = s.query(User).filter(User.username == username).first()
    token = user.create_access_token(conversation_id)
    win_curl = get_powershell(message, token, sender)
    posix_curl = posix(message, token, sender)
    json_curl = get_json(message, token, sender)
    msg = f"""Send Transmission to: {channel_name}\n\nWindoze:```\n{win_curl}\n```\nPosix:\n```\n{posix_curl}\n```\nHTTP POST:```\n{json_curl}\n```"""
    return msg


def extract_message_sender(command, event_body):
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