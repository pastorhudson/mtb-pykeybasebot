import requests
import random
import json
from fuzzywuzzy import fuzz

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_drwho(ep):

    if is_int(ep):
        url = f'https://api.catalogopolis.xyz/v1/episodes/{ep}'

        response = requests.request("GET", url, headers=None, data=None)

        try:
            ep_data = response.json()
        except json.decoder.JSONDecodeError:
            return f"There is no episode: {ep}.\nAnd you said you were a Dr Who Fan. . . :expressionless:"
    else:
        url = f'https://api.catalogopolis.xyz/v1/episodes'
        response = requests.request("GET", url, headers=None, data=None)

        last_ratio = 0
        for episode in response.json():
            try:
                # print(episode['title'])
                ratio = (fuzz.partial_ratio(episode['title'], ep))
                if ratio > last_ratio:
                    ep_data = episode
                    last_ratio = ratio
            except Exception as e:
                print(e)


    observations = [
        "Now I'm watching TV. . . ",
        "What I wouldn't give to be a Dalek. . .",
        "I miss Rose. . ."
    ]
    msg = f"{random.choice(observations)}```"
    msg += f"Title: {ep_data['title']}\n" \
           f"Episode ID: {ep_data['id']}\n" \
           f"Air Date: {ep_data['originalAirDate']}\n" \
           f"Run Time: {ep_data['runtime']}\n" \
           f"```"

    return msg


if __name__ == "__main__":
    print(get_drwho("the bells"))
