import requests
import json


def get_cow(msg):
    payload = {}
    headers = {}
    url = f"https://marvn.app/say?msg={msg}"
    response = requests.request("GET", url, headers=headers, data=payload)
    cow_said = response.json()

    return cow_said['message']


if __name__ == "__main__":
    print(get_cow("YOU ARE MY SUNSHINE"))
