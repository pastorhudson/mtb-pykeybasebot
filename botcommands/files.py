from pathlib import Path
import os
import json


def get_files():
    storage = Path('./uploads/')
    links = []
    msg = "Oh sure make marvn hang on to the files\n" \
          f"{os.environ.get('YOUTRANSFER_URL')}\n" \
          f"User: {os.environ.get('YOUTRANSFER_USER')} Pass: {os.environ.get('YOUTRANSFER_PASS')}"
    for file in list(storage.glob('**/*.json')):
        with open(file) as f:
            data = json.load(f)

            print(data)
            try:
                if data['link'] not in links:
                    link = data['link'].split('//')[0] + "//" + str(os.environ.get('YOUTRANSFER_USER')) + \
                           ":" + str(os.environ.get('YOUTRANSFER_PASS')) + "@" + data['link'].split('//')[1]
                    msg += f"```{data['name']} {data['filesize']}```\n" \
                           f"{link}\n\n"
                    links.append(data['link'])
            except KeyError:
                if data['files'][0]['link'] not in links:
                    link = data['files'][0]['link'].split('//')[0] + "//" + str(os.environ.get('YOUTRANSFER_USER')) + \
                           ":" + str(os.environ.get('YOUTRANSFER_PASS')) + "@" + data['files'][0]['link'].split('//')[1]
                    msg += f"```{data['files'][0]['name']} {data['files'][0]['filesize']}```\n" \
                           f"{link}\n\n"
                    links.append(data['files'][0]['link'])
    return msg


if __name__ == "__main__":
    print(get_files())
