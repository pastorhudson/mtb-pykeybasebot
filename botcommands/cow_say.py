import requests
import random

def get_cow(msg):
    payload = {}
    headers = {}
    url = f"https://marvn.app/say?msg={msg}"
    response = requests.request("GET", url, headers=headers, data=payload)

    observations = [
        "I can't believe you've done this.",
        "This is a new low.",
        "I'm so embarrassed.",
        "What were you thinking? You monster. . . "
    ]

    msg = random.choice(observations)
    msg += f"```{response.text}```"
    return msg


if __name__ == "__main__":
    print(get_cow("YOU ARE MY SUNSHINE"))
