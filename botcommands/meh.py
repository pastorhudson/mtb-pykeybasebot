import feedparser
import random
import requests
from pathlib import Path

storage = Path('./storage')
print(storage.absolute())


def download_img(pic_url):
    # with storage.open('wb') as handle:
    with open(f"{storage.absolute()}/meh.png", 'wb') as handle:
            response = requests.get(pic_url, stream=True)

            if not response.ok:
                pass

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
    return "meh.png"


def get_observation():
    observations = [
        "Now I'm doing the shopping. . . ",
        "Where did it all go wrong?",
        "Meh.",
        "I'd snatch that up.",
        "Nobody is going to buy this."
    ]
    return random.choice(observations)


def get_meh(observation=True):
    meh = feedparser.parse('https://meh.com/deals.rss')
    msg = ""
    if observation:
        msg = get_observation()
    msg += "```"

    msg += meh['entries'][0]['title']
    img = meh['entries'][0]['summary'].split('=')[1].split('"')[1]

    msg += "```\n"
    msg += meh['entries'][0]['links'][0]['href'] + "\n"
    download_img(img)
    return msg


if __name__ == '__main__':
    print(get_meh(observation=False))
