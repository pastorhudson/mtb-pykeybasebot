import requests
import random


def _fetch_bleach():
    url = "https://api.reddit.com/r/eyebleach/random/.json?is_gallery=False"
    response = requests.get(url, headers={'User-agent': 'mtb-keybasebot 0.1'})
    try:
        print(response.json()[0]["data"]["children"][0]["data"]["is_gallery"])
        return False, response
    except KeyError:
        return True, response


def get_eyebleach_data(count):
    if abs(count) > 11:
        count = 11

    eyebleach = {}
    for bleach in range(abs(count)):

        is_gallery = False
        while not is_gallery:
            is_gallery, response = _fetch_bleach()

        try:
            eyebleach[f'{response.json()[0]["data"]["children"][0]["data"]["name"]}'] = response.json()[0]["data"]["children"][0]["data"]
        except Exception as e:
            print("in the except")

            print(e)
    return eyebleach


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
    for bleach in get_eyebleach_data(bleach_level).items():
        msg += bleach[1]["url"] + "\n"
    return msg


if __name__ == "__main__":
    # a = abs("3")
    pass

