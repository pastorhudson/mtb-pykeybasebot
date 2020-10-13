import requests
import json


def get_cow(msg):
    payload = {}
    headers = {}
    url = f"https://marvn.app/say?msg={msg}"
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


if __name__ == "__main__":
    print(get_cow("YOU ARE MY SUNSHINE"))
