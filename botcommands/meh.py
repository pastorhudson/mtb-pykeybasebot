import feedparser
import random


def get_observation():
    observations = [
        "Now I'm doing the shopping. . . \n",
        "Where did it all go wrong?\n",
        "Meh.\n",
        "I'd snatch that up.\n",
        "Nobody is going to buy this.\n"
    ]
    return random.choice(observations)


def get_meh(observation=True):
    meh = feedparser.parse('https://meh.com/deals.rss')
    msg = ""
    if observation:
        msg = get_observation()
    msg += "`"

    msg += meh['entries'][0]['title']

    msg += "` "
    msg += meh['entries'][0]['links'][0]['href']
    return msg


if __name__ == '__main__':
    print(get_meh(observation=False))
