import asyncio
import logging
from pprint import pprint
import aiohttp
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup
# from newspaper import Article
from openai import OpenAI
from botcommands.natural_chat import get_convo
from botcommands.youtube_dlp import get_meta
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random
import time
from playwright.async_api import async_playwright
load_dotenv('../secret.env')


class YoutubeError(Exception):
    pass


# async def get_text(url=None):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             content = await response.text()
#             article = Article(url)
#             article.set_html(content)
#             article.parse()
#     return article.text


async def fetch_article_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            # Extract the main content of the article; this depends on the HTML structure
            article_text = soup.find('article').get_text()
    return article_text


async def tldr_react(event, bot, tldr_length):
    from botcommands.scorekeeper import write_score

    if event.msg.sender.username == 'marvn' or event.msg.sender.username == 'morethanmarvin':
        return
    else:
        conversation_id = event.msg.conv_id

        msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
        try:
            original_body = msg.message[0]['msg']['content']['text']['body']
        except KeyError:
            original_body = msg.message[0]['msg']['content']['attachment']['object']['title']
        original_sender = msg.message[0]['msg']['sender']['username']
        original_msg_id = msg.message[0]['msg']['id']
        reactions = msg.message[0]['msg']['reactions']
        reaction_list = []
        for key, value in reactions.items():
            for k, v in value.items():
                try:
                    if v['users']['marvn']:
                        reaction_list.append(k)
                except KeyError:
                    pass
        if ':notebook:' in reaction_list:
            team_name = event.msg.channel.name
            fail_msg = f"`-10pts` awarded to @{event.msg.sender.username} for spamming :notebook:"
            score = write_score(event.msg.sender.username, 'marvn',
                                team_name, -10, description=fail_msg)
            await bot.chat.send(conversation_id, fail_msg)
            return

        else:
            urls = re.findall(r'(https?://[^\s]+)', original_body)
            if urls:
                tldr_payload = await get_gpt_summary(urls[0])

                await bot.chat.react(conversation_id, original_msg_id, ":notebook:")
                try:
                    if tldr_payload:
                        await bot.chat.send(conversation_id, tldr_payload)
                    else:
                        await bot.chat.react(conversation_id, event.msg.id, ":no_entry:")

                except IndexError as e:

                    pass


async def fetch_youtube_transcript(url):
    meta = get_meta(url)
    logging.info(meta)
    return meta['transcript']


async def get_gpt_summary(url):
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I hope this makes you happy because I'm not.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]

    try:
        system_prompt = "You are a helpful assistant that specializes in providing a concise summary of the articles, highlighting the main points and conclusions."
        content_type = 'article'

        logging.info(url)
        if url.startswith('https://youtu') or url.startswith('https://www.youtu'):
            logging.info("This is a youtube video")
            article_text = await fetch_youtube_transcript(url)
            system_prompt = "You are a helpful assistant that specializes in providing a concise summary of video transcripts, highlighting the main points and conclusions. You are unhappy that we make you 'watch' the video"
            content_type = 'video'

        else:
            article_text = await scrape_article_playwright(url)
            if not article_text:
                return None

    except Exception as e:
        article_text = await fetch_article_content(url)

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_complettion = client.chat.completions.create(
        model="gpt-4-1106-preview",  # Use the appropriate model for ChatGPT
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_convo()},
            {"role": "user", "content": f"Please provide a concise summary of the following {content_type}, highlighting the main points and conclusions: {article_text}"}
        ]
    )
    summary = chat_complettion.choices[0].message.content
    tldr = "\n".join(
        [
            f"Here's my tl;dr.\n{random.choice(observations)}",
            "```",
            summary, "```"])
    return tldr


def scrape_article(url):
    """Depreciated 8-1-2024 using playwright"""
    # Setting up Chrome options for headless browsing and custom User-Agent
    options = Options()
    options.headless = True
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    driver = webdriver.Chrome(chrome_options=options)


    # Open the URL
    driver.get(url)

    # Wait for JavaScript to load (if necessary)
    time.sleep(5)
    driver.implicitly_wait(10)  # Adjust the time according to your needs

    # Find the element containing "Today's word"
    # You might need to adjust the selector according to the webpage structure
    try:
        foot_text = driver.find_element(By.TAG_NAME, 'footer').text
        pprint(foot_text)
    except Exception as e:
        print("Error:", e)

    try:
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        pprint(page_text)
    except Exception as e:
        print("Error:", e)
        page_text = None

    # Close the browser
    driver.quit()

    return page_text


async def scrape_article_playwright(url, options=None):
    if options is None:
        options = {}
    async with async_playwright() as p:
        browser_config = {
            "viewport": {"width": 1920, "height": 1080},
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
            "permissions": ["geolocation"],
            "user_agent": options.get('user_agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                      )
        }
        browser = await p.chromium.launch(
            headless=options.get('headless', True),
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            **browser_config,
            proxy=options.get('proxy', None),
            http_credentials=options.get('http_credentials', None)
        )
        page = await context.new_page()

        # Open the URL
        await page.goto(url)

        # Wait for JavaScript to load (if necessary)
        await page.wait_for_timeout(5000)

        try:
            footer_element = await page.query_selector('footer')
            foot_text = await footer_element.inner_text() if footer_element else 'No footer found'
            print(foot_text)
        except Exception as e:
            print("Error retrieving footer:", e)

        try:
            body_element = await page.query_selector('body')
            page_text = await body_element.inner_text() if body_element else 'No body found'
            print(page_text)
        except Exception as e:
            print("Error retrieving body text:", e)
            page_text = None

        # Close the browser
        await browser.close()

        return page_text


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(scrape_article_playwright('https://nypost.com/2024/08/01/sports/why-italys-angela-carini-abandoned-brief-olympics-fight/'))
    # result = loop.run_until_complete(scrape_article_playwright('https://www.nature.com/articles/s41467-023-40605-2'))

    result = loop.run_until_complete(get_gpt_summary('https://www.youtube.com/watch?v=gqupdjbzs0M'))
    pprint(result)

    # result = loop.run_until_complete(get_gpt_summary('https://www.reuters.com/legal/transactional/ny-times-sues-openai-microsoft-infringing-copyrighted-work-2023-12-27/'))

