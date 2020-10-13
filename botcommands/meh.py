import feedparser
import random


def get_meh():
    meh = feedparser.parse('https://meh.com/deals.rss')

    print(meh['entries'][0]['links'][0]['href'])

    observations = [
        "Now I'm doing the shopping. . . ",
        "Where did it all go wrong?",
        "Meh.",
        "I'd snatch that up.",
        "Nobody is going to buy this."
    ]

    msg = random.choice(observations)
    msg += "```\n"

    msg += meh['entries'][0]['title']


    msg += "\n```"
    msg += meh['entries'][0]['links'][0]['href']
    return msg


if __name__ == '__main__':
    print(get_meh())
