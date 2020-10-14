import requests
import random


def get_chuck(name=None, channel=None):
    """{'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}],
     'admins': [], 'writers': [{'uid': '7d368eae6a7292b4215ca46da021b919', 'username': 'sakanakami', 'fullName': 'Joe Eafrati'},
      {'uid': 'b3543e75d25a5b5b45e551c3cccf0e19', 'username': 'ihuman', 'fullName': 'Ethan Connor'}],
       'readers': [], 'bots': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin',
        'fullName': ''}, {'uid': 'ae0918c8e416811c7e6a4a737d39b119', 'username': 'marvn', 'fullName': ''}],
         'restrictedBots': [{'uid': '228b5863ba9c6a97c2103f7d5f59bf19', 'username': 'rssbot', 'fullName': 'RSS Bot'}]}"""


    print(channel)
    print(type(channel))
    joke_names = []
    for owners in channel['owners']:
        joke_names.append(owners['username'])
    for admins in channel['admins']:
        if admins['username'] not in joke_names:
            joke_names.append(admins['username'])
    for writers in channel['writers']:
        if writers['username'] not in joke_names:
            joke_names.append(writers['username'])
    for readers in channel['readers']:
        if readers['username'] not in joke_names:
            joke_names.append(readers['username'])
    print(joke_names)



