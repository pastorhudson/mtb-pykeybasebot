import requests
import random

def get_drwho(ep_number):
    url = f'https://api.catalogopolis.xyz/v1/episodes/{ep_number}'

    response = requests.request("GET", url, headers=None, data=None)

    print(response.json())
    ep = response.json()
    observations = [
        "Now I'm watching TV. . . ",
        "What I wouldn't give to be a Dalek. . .",
        "I miss Rose. . ."
    ]
    msg = f"{random.choice(observations)}```"

    msg += f"Title: {ep['title']}\n" \
           f"Air Date: {ep['originalAirDate']}\n" \
           f"Run Time: {ep['runtime']}\n" \
           f"```"

    return msg


if __name__ == "__main__":
    print(get_drwho(780))
