import feedparser
import random
from pathlib import Path
from newspaper import Article
from botcommands.natural_chat import get_chat_with_image
import aiohttp
import asyncio

# from dotenv import load_dotenv

storage = Path('./storage')
print(storage.absolute())


# def download_img(pic_url):
#     # with storage.open('wb') as handle:
#     with open(f"{storage.absolute()}/meh.png", 'wb') as handle:
#             response = requests.get(pic_url, stream=True)
#
#             if not response.ok:
#                 pass
#
#             for block in response.iter_content(1024):
#                 if not block:
#                     break
#
#                 handle.write(block)
#     return "meh.png"


async def download_img(pic_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(pic_url) as response:
            if response.status != 200:
                return None

            file_path = f"{storage.absolute()}/meh.png"

            with open(file_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            return "meh.png"


async def get_observation():
    try:
        return await get_chat_with_image(f"{storage.absolute()}/meh.png", "This is a daily deal can you tell us about the product and weather or not it is worth purchasing? If it is underwelming then use the word 'meh' excessively.")
    except Exception as e:
        print(e)
        observations = [
            "Now I'm doing the shopping. . . ",
            "Where did it all go wrong?",
            "Meh.",
            "I'd snatch that up.",
            "Nobody is going to buy this."
        ]
        return random.choice(observations)


async def get_meh(observation=True):
    meh = feedparser.parse('https://meh.com/deals.rss')
    await download_img(await get_image())

    msg = ""
    if observation:
        msg = await get_observation()
    msg += "\n```"

    msg += meh['entries'][0]['title']
    img = meh['entries'][0]['summary'].split('=')[1].split('"')[1]

    msg += "```\n"
    msg += meh['entries'][0]['links'][0]['href'] + "\n"
    return msg


async def get_image():
    article = Article('https://meh.com')
    article.download()
    article.parse()
    # print(article.title)
    # print(article.text)
    return article.top_img


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_meh(observation=True))

    # get_image()
    print(result)
