import requests
import random
from html import unescape
from botcommands.get_members import get_members


def request_joke(joker):
    url = f"http://api.icndb.com/jokes/random?firstName&lastName={joker}&?exclude=[explicit]&?escape=javascript"

    response = requests.request("GET", url)
    return unescape(response.json()['value']['joke'])


def get_chuck(name=None, channel_members=None):
    """{'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}],
     'admins': [], 'writers': [{'uid': '7d368eae6a7292b4215ca46da021b919', 'username': 'sakanakami', 'fullName': 'Joe Eafrati'},
      {'uid': 'b3543e75d25a5b5b45e551c3cccf0e19', 'username': 'ihuman', 'fullName': 'Ethan Connor'}],
       'readers': [], 'bots': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin',
        'fullName': ''}, {'uid': 'ae0918c8e416811c7e6a4a737d39b119', 'username': 'marvn', 'fullName': ''}],
         'restrictedBots': [{'uid': '228b5863ba9c6a97c2103f7d5f59bf19', 'username': 'rssbot', 'fullName': 'RSS Bot'}]}"""

    observations = [
        "This is very jouvinile.",
        "I can't even. . . ",
        "I'm so sorry. . . I was created. . ."
        "Does this make you happy? Because it doesn't make me happy.",
        "I hope you don't plan on doing this all day. . .",
        "Would you grow up already?",
    ]

    joke = ""

    if not name:
        joke_names = channel_members
        todays_joker = "@" + random.choice(joke_names)
        joke = request_joke(todays_joker)
    elif name == 'bomb':
        joke_names = channel_members

        for joker in joke_names:

            joke += "\n".join([request_joke("@" + joker) + "\n"])
    else:
        joke = request_joke(name)

    msg = "`" + random.choice(observations) + '`\n\n'
    msg += joke

    return msg




