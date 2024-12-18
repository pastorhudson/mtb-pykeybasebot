from pprint import pprint
import os
import requests
import random


def _fetch_bleach(count):
    try:
        if abs(count) > 11:
            count = 11
    except Exception as e:
        count = 5
    try:
        url = f"https://api.thecatapi.com/v1/images/search?limit={abs(count)}"
        response = requests.get(url, headers={'x-api-key': os.environ['CAT-API-KEY']})
        return response.json()
    except Exception as e:
        return []


def get_eyebleach(bleach_level=3):

    observations = [
        "Moving right along. . . ",
        "And now for a pallet cleansing. . .",
        "@alexius knock it off.",
        "Do you kiss your mother with that url?",
        "Oh sure I'll just go fetch a picture for you master. . . :face_with_rolling_eyes:"
    ]

    msg = random.choice(observations) + "\n"
    # msg_list = []
    bleach_list = _fetch_bleach(bleach_level)
    if bleach_list:
        for bleach in bleach_list:
            msg += bleach["url"] + "\n"
    else:
        msg = 'No Bleach for you.'
    return msg


if __name__ == "__main__":

    print(get_eyebleach("f"))
    pass
