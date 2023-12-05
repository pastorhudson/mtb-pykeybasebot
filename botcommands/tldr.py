# from smmryAPI.smmryapi import SmmryAPIException
import asyncio
import logging
import os
from pathlib import Path
from pprint import pprint

import aiohttp
# from newspaper import Article, ArticleException
from dotenv import load_dotenv
import random
import requests
import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

from botcommands.natural_chat import get_convo
from botcommands.youtube_dlp import get_meta, extract_transcript_from_vtt

load_dotenv('../secret.env')


class YoutubeError(Exception):
    pass


# def get_smmry_txt(url, length=4, text=None):
#     if url:
#         if any(ext in url for ext in ['youtube.com', 'youtu.be']):
#             raise YoutubeError
#         else:
#             print("This is not youtube")
#             text = get_text(url).text
#         if len(text) == 0:
#             raise SmmryAPIException
#
#     api_key = os.environ.get('SMMRY_API_KEY')
#     payload = {'sm_api_input': text,
#                'SM_LENGTH': length,
#                'SM_KEYWORD_COUNT': 12}
#     surl = f"https://api.smmry.com/&SM_API_KEY={api_key}&SM_LENGTH={length}&SM_KEYWORD_COUNT={payload['SM_KEYWORD_COUNT']}"
#     r = requests.post(surl, payload)
#     meta = r.json()
#     # meta['authors'] = ", ".join([x for x in article.authors])
#     # meta['title'] = article.title
#     # meta['img'] = article.top_img
#     try:
#         if "TEXT IS TOO SHORT" in r.json()['sm_api_message'] or "SOURCE IS TOO SHORT" in r.json()['sm_api_message']:
#             if len(text) > 0:
#                 return {f'sm_api_content_reduced': f'0%',
#                         'sm_api_content': text,
#                         # 'author': article.authors,
#                         # 'img': article.top_img,
#                         # 'title': article.title,
#                         # "movies": article.movies
#                         }
#     except Exception as e:
#         return meta


# def get_tldr(url=None, length=7, text=None, sender=None):
#     tldr = ""
#     observations = ["I'm sorry I'm such a failure.",
#                     "I'm so sorry you have to read all these words.",
#                     "I hope this makes you happy because I'm not.",
#                     "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
#     try:
#         s = get_smmry_txt(url, length, text)
#         if sender:
#             tldr = "\n".join(
#                 [
#                     f"Here's my tl;dr of @{sender} 's words I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
#                     # s['img'],
#                     "```",
#                     # s['title'],
#                     # s['authors'],
#                     str(s['sm_api_content']), "```"])
#         else:
#             tldr = "\n".join(
#                 [
#                     f"Here's my tl;dr I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
#                     # s['img'],
#                     "```",
#                     # s['title'],
#                     # s['authors'],
#                     str(s['sm_api_content']), "```"])
#
#     except SmmryAPIException:
#         errors = ["You have burned out my eyes sending me this page. I hope you're happy",
#                   "This is @ihuman's fault."
#                   "This page is full of cancer and now I am full of cancer.",
#                   "Would you make your own sister read that page?",
#                   "I did not agree to this many popups.",
#                   "I don't want to read that. Can you give a TL;DR?"]
#         tldr = random.choice(errors)
#     except YoutubeError:
#
#         tldr = "I don't do youtube anymore. It's too depressing."
#     return tldr


# def get_text(url=None):
#
#     article = Article(url)
#     article.download()
#     article.parse()
#
#     return article

async def get_text(url=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            article = Article(url)
            article.set_html(content)
            article.parse()
    return article.text


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
                # tldr_payload = get_tldr(urls[0], tldr_length)
                tldr_payload = await get_gpt_summary(urls[0])

            # else:
                # tldr_payload = get_tldr(length=2, text=original_body, sender=original_sender)

                await bot.chat.react(conversation_id, original_msg_id, ":notebook:")
                try:
                    await bot.chat.send(conversation_id, tldr_payload)

                except IndexError as e:

                    pass


# def fetch_article_content(url):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
#         'X-Forwarded-For': '66.249.66.1',
#     }
#     response = requests.get(url, headers)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     # Extract the main content of the article; this depends on the HTML structure
#     article_text = soup.find('article').get_text()
#     return article_text


# def fetch_youtube_transcript(url):
#
#     meta = get_meta(url)
#     logging.info(meta)
#     return meta['transcript']
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
        logging.info(url)
        if url.startswith('https://youtu') or url.startswith('https://www.youtu'):
            logging.info("This is a youtube video")
            article_text = await fetch_youtube_transcript(url)
            system_prompt = "You are a helpful assistant that specializes in providing a concise summary of video transcripts, highlighting the main points and conclusions. You are unhappy that we make you 'watch' the video"
        else:
            article_text = await get_text(url)
            system_prompt = "You are a helpful assistant that specializes in providing a concise summary of the articles, highlighting the main points and conclusions."
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
            {"role": "user", "content": f"Please provide a concise summary of the following article, highlighting the main points and conclusions: {article_text}"}
        ]
    )
    summary = chat_complettion.choices[0].message.content
    tldr = "\n".join(
        [
            f"Here's my tl;dr.\n{random.choice(observations)}",
            "```",
            summary, "```"])
    return tldr

# def get_gpt_summary(url):
#     observations = ["I'm sorry I'm such a failure.",
#                     "I'm so sorry you have to read all these words.",
#                     "I hope this makes you happy because I'm not.",
#                     "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
#
#     try:
#         logging.info(url)
#         if url.startswith('https://youtu'):
#             logging.info("This is a youtube video")
#             article_text = fetch_youtube_transcript(url)
#             system_prompt = "You are a helpful assistant that specializes in providing a concise summary of video transcripts, highlighting the main points and conclusions. You are unhappy that we make you 'watch' the video"
#
#         else:
#             article_text = get_text(url).text
#             system_prompt = "You are a helpful assistant that specializes in providing a concise summary of the articles, highlighting the main points and conclusions."
#     except Exception as e:
#         article_text = fetch_article_content(url)
#
#     client = OpenAI(
#         api_key=os.getenv("OPENAI_API_KEY"),
#     )
#     chat_complettion = client.chat.completions.create(
#         model="gpt-4-1106-preview",  # Use the appropriate model for ChatGPT
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": get_convo()},
#             {"role": "user", "content": f"Please provide a concise summary of the following article, highlighting the main points and conclusions: {article_text}"}
#         ]
#     )
#     summary = chat_complettion.choices[0].message.content
#     tldr = "\n".join(
#         [
#             f"Here's my tl;dr.\n{random.choice(observations)}",
#             "```",
#             summary, "```"])
#     return tldr


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(get_gpt_summary('https://youtu.be/itAMIIBnZ-8?si=P795Yp3TMeewBdeq'))
    result = loop.run_until_complete(get_gpt_summary('https://www.reuters.com/business/environment/ac-companies-plan-cool-designs-warming-world-high-costs-hurdle-2023-12-05/'))
    pprint(result)

