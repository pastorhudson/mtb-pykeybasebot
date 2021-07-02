import requests
import random


def get_eyebleach_data(count=2):
    eyebleach = {}
    for bleach in range(count):
        url = "https://api.reddit.com/r/eyebleach/random/"
        response = requests.get(url, headers={'User-agent': 'mtb-keybasebot 0.1'})

        try:
            eyebleach[f'{response.json()[0]["data"]["children"][0]["data"]["name"]}'] = response.json()[0]["data"]["children"][0]["data"]
        except Exception as e:
            print(e)
    return eyebleach


def get_eyebleach(bleach_level=2):

    observations = [
        "Moving right along. . . ",
        "And now for a pallet cleansing. . .",
        "@alexius knock it off.",
        "Do you kiss your mother with that url?",
        "Oh sure I'll just go fetch a picture for you master. . . :eye_roll:"
    ]

    msg = random.choice(observations) + "\n"
    # print(get_eyebleach_data(bleach_level))
    for bleach in get_eyebleach_data(bleach_level).items():
        msg += bleach[1]["url"] + "\n"

    return msg


if __name__ == "__main__":
    print(get_eyebleach(4))
