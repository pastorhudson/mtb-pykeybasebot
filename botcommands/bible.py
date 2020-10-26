#!/usr/bin/env python

import sys
import requests
import os


API_KEY = os.environ.get('ESV_KEY')
API_URL = 'https://api.esv.org/v3/passage/text/'


def get_esv_text(passage):
    params = {
        'q': passage,
        'include-headings': False,
        'include-footnotes': False,
        'include-verse-numbers': False,
        'include-short-copyright': False,
        'include-passage-references': False
    }

    headers = {
        'Authorization': 'Token %s' % API_KEY
    }

    response = requests.get(API_URL, params=params, headers=headers)
    print(response.content)

    passages = response.json()['passages']

    return passages[0].strip() if passages else 'Error: Passage not found'


if __name__ == '__main__':
    passage = 'John 1:12'

    if passage:
        print(get_esv_text(passage))
