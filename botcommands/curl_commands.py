
def posix(conversation_id, message, sender):
    return f"""curl -X POST --location "https://marvn.app/add_message" \
    -H "Content-Type: application/json" \
    -d '{{
            "sender": "{sender}",
            "message": "{message}",
            "destination": "{conversation_id}"
        }}'"""


def get_powershell(conversation_id, message, sender):
    return f"""
    $url = 'https://marvn.app/add_message'
    $headers = @{{
        'Content-Type' = 'application/json'
    }}
    $body = @{{
        'sender' = '{sender}'
        'message' = '{message}'
        'destination' = '{conversation_id}'
    }} | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body
    """

def get_json(conversation_id, message, sender):
    return f"""POST https://marvn.app/add_message
Content-Type: application/json

{{
  "sender" = "{sender}"
  "message": "{message}",
  "destination": "{conversation_id}"
}}"""


def get_curl(conversation_id, message, sender):
    win_curl = get_powershell(conversation_id, message, sender)
    posix_curl = posix(conversation_id, message, sender)
    json_curl = get_json(conversation_id, message, sender)
    msg = f"""Windoze:```\n{win_curl}\n```\nPosix:\n```\n{posix_curl}\n```\nHTTP POST:```\n{json_curl}\n```"""
    return msg


if __name__ == "__main__":
    print(get_curl("123", "Hello World", "github.com"))