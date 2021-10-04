from pathlib import Path
import os
import json


def get_files():
    storage = Path('./uploads/')
    print(storage.absolute())
    links = []
    msg = "Oh sure make marvn hang on to the files\n" \
          f"{'YOUTRANSFER_URL'}\n" \
          f"User: {os.environ.get('YOUTRANSFER_USER')} Pass: {os.environ.get('YOUTRANSFER_PASS')}"
    for file in list(storage.glob('**/*.json')):
        print(links)
        with open(file) as f:
            data = json.load(f)

            print(data)
            try:
                if data['link'] not in links:
                    msg += f"```{data['name']} {data['filesize']}```\n" \
                           f"{data['link']}\n\n"
                    links.append(data['link'])
            except KeyError:
                if data['files'][0]['link'] not in links:
                    msg += f"```{data['files'][0]['name']} {data['files'][0]['filesize']}```\n" \
                           f"{data['files'][0]['link']}\n\n"
                    links.append(data['files'][0]['link'])
    return msg


if __name__ == "__main__":
    print(get_files())
