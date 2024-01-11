
def posix(conversation_id, message):
    return f"""curl -X POST --location "https://marvn.app/add_message" \
    -H "Content-Type: application/json" \
    -d '{{
            "message": "{message}",
            "destination": "{conversation_id}"
        }}'"""


def windows(conversation_id, message):
    curl = """curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{\"message\": \""""
    curl += message
    curl += """\", \"destination\": \""""
    curl += conversation_id
    curl += """\"}"""
    return curl


def get_curl(conversation_id, message):
    win_curl = windows(conversation_id, message)
    posix_curl = posix(conversation_id, message)
    msg = f"""Widnows:```\n{win_curl}```\n```{posix_curl}```"""
    return msg


if __name__ == "__main__":
    print(get_curl("123", "Hello World"))
