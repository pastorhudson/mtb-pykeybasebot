#!/usr/bin/env python

import sys
import requests
import os


def get_esv_text(passage):
    API_KEY = os.environ.get('ESV_KEY')
    API_URL = 'https://api.esv.org/v3/passage/text/'
    params = {
        'q': passage,
        'include-headings': False,
        'include-footnotes': False,
        'include-verse-numbers': True,
        'include-short-copyright': True,
        'include-passage-references': True
    }

    headers = {
        'Authorization': 'Token %s' % API_KEY
    }

    response = requests.get(API_URL, params=params, headers=headers)
    print(response.json())

    if response.json()['passages']:
        passages = response.json()
        msg = "```"
        msg += "".join(passages['passages']) + "```"

        return msg if passages else 'Error: Passage not found'

    else:
        API_URL = 'https://api.esv.org/v3/passage/search/'
        response = requests.get(API_URL, params=params, headers=headers)
        msg = ""
        for result in response.json()['results']:
            msg += "```" + result['reference'] + "\n" + result['content'] + "```\n"

        return msg


if __name__ == '__main__':
    passage = 'baptized'
    if passage:
        print(get_esv_text(passage))
