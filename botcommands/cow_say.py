import requests
import random
import json
from botcommands.cow_characters import get_characters


def get_cow(msg):
    characters = get_characters()

    """faces     'default' => ["oo", "  "],
    'borg' => ["==", "  "],
    'dead' => ["==", "U "],
    'greedy' => ["$$", "  "],
    'paranoid' => ["@@", "  "],
    'stoned' => ["**", "U "],
    'tired' => ["--", "  "],
    'wired' => ["OO", "  "],
    'young' => ["..", "  "]
    """

    character = "cow"
    if msg.split(" ")[0] in characters:
        character = msg.split(" ")[0]
        char_length = len(character) + 1
        msg = msg[char_length:]
    url = "https://marvn.app/say"
    payload = {"message": msg, "cow": character, "balloon_type": "say", "face_type": "default"}
    # payload = {"message": msg}
    response = requests.post(url, json=payload)

    observations = [
        "I can't believe you've done this.",
        "This is a new low.",
        "I'm so embarrassed.",
        "What were you thinking? You monster. . . "
    ]
    msg = random.choice(observations)
    msg += f"```{response.json()['message']}```"
    return msg


if __name__ == "__main__":
    print(get_cow("beavis.zen YOU ARE MY SUNSHINE"))
