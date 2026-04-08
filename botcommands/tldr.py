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
from camoufox.async_api import AsyncCamoufox

import random
import time
from playwright.async_api import async_playwright
load_dotenv('../secret.env')


class YoutubeError(Exception):
    pass


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
    observations = [
        "I'm sorry I'm such a failure.",
        "I'm so sorry you have to read all these words.",
        "I hope this makes you happy because I'm not.",
        "Now I'm stuck remembering this useless article forever. I hope it was worth it."
    ]

    system_prompt = "You are a helpful assistant that summarizes content concisely."

    try:
        if "youtu" in url:
            article_text = await fetch_youtube_transcript(url)
            content_type = "video"
        else:
            article_text = None

            try:
                article_text = await scrape_article_playwright(url)
            except Exception as e:
                logging.warning(f"Playwright failed: {e}")

            if not article_text:
                try:
                    article_text = await fetch_article_content(url)
                except Exception as e:
                    logging.warning(f"Fallback scrape failed: {e}")

            if not article_text:
                return "Couldn't extract article content."

            content_type = "article"

    except Exception as e:
        logging.error(f"Error extracting content: {e}")
        return "Error processing content."

    # truncate
    article_text = article_text[:12000]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_convo()},
            {"role": "user", "content": f"Summarize this {content_type}: {article_text}"}
        ]
    )

    summary = response.output_text

    return "\n".join([
        f"Here's my tl;dr.\n{random.choice(observations)}",
        "```",
        summary,
        "```"
    ])

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



# async def scrape_article_playwright(url, options=None):
#     async with AsyncCamoufox(headless=True, geoip=True) as browser:
#         page = await browser.new_page()
#         await page.goto(url, wait_until="networkidle")
#         await page.wait_for_timeout(random.randint(2000, 4000))
#         body = await page.query_selector('body')
#         return await body.inner_text() if body else None


async def scrape_article_playwright(url, options=None):
    async with AsyncCamoufox(headless=True, geoip=True) as browser:
        page = await browser.new_page()

        # Abort heavy assets you don't need for text scraping
        await page.route("**/*.{png,jpg,jpeg,gif,svg,mp4,woff2,woff}",
                         lambda route: route.abort())

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            # Fall back if networkidle times out (common on ad-heavy sites)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception as e:
                return None

        # Scroll to trigger lazy-loaded content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await page.wait_for_timeout(random.randint(2000, 4000))

        # Dismiss common overlays (cookie banners, modals)
        for selector in ["[id*='cookie'] button", "[class*='modal'] button[class*='close']",
                         "[aria-label='Close']", "button[class*='dismiss']"]:
            try:
                el = await page.query_selector(selector)
                if el:
                    await el.click()
                    await page.wait_for_timeout(500)
            except Exception:
                pass

        # Prefer <article> or <main> over raw body for cleaner text
        for selector in ["article", "main", "[role='main']", "body"]:
            el = await page.query_selector(selector)
            if el:
                text = await el.inner_text()
                if text and len(text.strip()) > 200:  # sanity-check it's real content
                    return text.strip()

        return None

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(scrape_article_playwright('https://nypost.com/2024/08/01/sports/why-italys-angela-carini-abandoned-brief-olympics-fight/'))
    # result = loop.run_until_complete(scrape_article_playwright('https://www.nature.com/articles/s41467-023-40605-2'))

    # result = loop.run_until_complete(get_gpt_summary('https://youtu.be/mpAHFlZqIKw?si=RO_hrUT8YN6t3-up'))

    # result = loop.run_until_complete(get_gpt_summary('https://apnews.com/article/cuba-us-congress-jayapal-jackson-92db6e9bfebfb70f3c0b29a42a40c8fa'))
    result = loop.run_until_complete(
        get_gpt_summary('https://www.nbcnews.com/world/iran/live-blog/live-updates-iran-war-trump-deadline-hormuz-infrastructure-ceasefire-rcna267039'))
    pprint(result)

