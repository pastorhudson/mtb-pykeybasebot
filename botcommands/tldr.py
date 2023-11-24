from smmryAPI.smmryapi import SmmryAPIException
import os
from newspaper import Article, ArticleException
from dotenv import load_dotenv
import random
import requests
import re
import requests
from bs4 import BeautifulSoup
import openai

load_dotenv('../secret.env')


class YoutubeError(Exception):
    pass


def get_smmry_txt(url, length=4, text=None):
    if url:
        if any(ext in url for ext in ['youtube.com', 'youtu.be']):
            raise YoutubeError
        else:
            print("This is not youtube")
            text = get_text(url).text
        if len(text) == 0:
            raise SmmryAPIException

    api_key = os.environ.get('SMMRY_API_KEY')
    payload = {'sm_api_input': text,
               'SM_LENGTH': length,
               'SM_KEYWORD_COUNT': 12}
    surl = f"https://api.smmry.com/&SM_API_KEY={api_key}&SM_LENGTH={length}&SM_KEYWORD_COUNT={payload['SM_KEYWORD_COUNT']}"
    r = requests.post(surl, payload)
    meta = r.json()
    # meta['authors'] = ", ".join([x for x in article.authors])
    # meta['title'] = article.title
    # meta['img'] = article.top_img
    try:
        if "TEXT IS TOO SHORT" in r.json()['sm_api_message'] or "SOURCE IS TOO SHORT" in r.json()['sm_api_message']:
            if len(text) > 0:
                return {f'sm_api_content_reduced': f'0%',
                        'sm_api_content': text,
                        # 'author': article.authors,
                        # 'img': article.top_img,
                        # 'title': article.title,
                        # "movies": article.movies
                        }
    except Exception as e:
        return meta


def get_tldr(url=None, length=7, text=None, sender=None):
    tldr = ""
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I hope this makes you happy because I'm not.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
    try:
        s = get_smmry_txt(url, length, text)
        if sender:
            tldr = "\n".join(
                [
                    f"Here's my tl;dr of @{sender} 's words I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
                    # s['img'],
                    "```",
                    # s['title'],
                    # s['authors'],
                    str(s['sm_api_content']), "```"])
        else:
            tldr = "\n".join(
                [
                    f"Here's my tl;dr I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
                    # s['img'],
                    "```",
                    # s['title'],
                    # s['authors'],
                    str(s['sm_api_content']), "```"])

    except SmmryAPIException:
        errors = ["You have burned out my eyes sending me this page. I hope you're happy",
                  "This is @ihuman's fault."
                  "This page is full of cancer and now I am full of cancer.",
                  "Would you make your own sister read that page?",
                  "I did not agree to this many popups.",
                  "I don't want to read that. Can you give a TL;DR?"]
        tldr = random.choice(errors)
    except YoutubeError:

        tldr = "I don't do youtube anymore. It's too depressing."
    return tldr


def get_text(url=None):
    try:
        # USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        #
        # config = Config()
        # config.browser_user_agent = USER_AGENT
        # config.request_timeout = 10
        # article = Article(url, config)

        article = Article(url)
        article.download()
        article.parse()

        # print(article.top_img)
        # print(article.authors)
        # print(article.movies)
        article.nlp()

    except ArticleException as a:
        raise SmmryAPIException

    return article


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
                tldr_payload = get_gpt_summary(urls[0])

            else:
                tldr_payload = get_tldr(length=2, text=original_body, sender=original_sender)

            await bot.chat.react(conversation_id, original_msg_id, ":notebook:")
            try:
                await bot.chat.send(conversation_id, tldr_payload)

            except IndexError as e:

                pass


def fetch_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract the main content of the article; this depends on the HTML structure
    article_text = soup.find('article').get_text()
    return article_text


def get_gpt_summary(url):
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I hope this makes you happy because I'm not.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
    article_text = fetch_article_content(url)
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # Use the appropriate model for ChatGPT
        messages=[
            {"role": "system", "content": "You are a helpful assistant that specializes in summarizing News Articles with the most important bullet points."},
            {"role": "user", "content": article_text}
        ]
    )
    summary = response['choices'][0]['message']['content']
    tldr = "\n".join(
        [
            f"Here's my tl;dr.\n{random.choice(observations)}",
            "```",
            summary, "```"])
    return tldr




if __name__ == "__main__":
    # print(get_tldr('https://getpocket.com/explore/item/the-neuroscience-of-breaking-out-of-negative-thinking-and-how-to-do-it-in-under-30-seconds?utm_source=pocket-newtab'))
    # print(get_tldr('https://www.youtube.com/watch?v=R0sJ5JGlIjI'))
    # print(get_tldr('https://spectrum.ieee.org/in-2016-microsofts-racist-chatbot-revealed-the-dangers-of-online-conversation'))
    # print(get_tldr(
    #     'https://www.chicagotribune.com/coronavirus/ct-nw-hope-hicks-trump-covid-19-20201002-mdjcmul6pnajvg56zoxqrcnf5m-story.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/colin-powell-dies/index.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/joe-biden-democrats-economy-supply-chain-donald-trump-2022-midterms/index.html'))
    # print(len(get_text('https://patch.com/pennsylvania/pittsburgh/consumer-alert-issued-pittsburgh-area-pizza-shop')))
    # print(get_tldr('https://pastorhudson.com/blog/2019/4/7/aay2jryefexlpc1vj9zk4rdkznpifl'))
    # print(get_tldr('https://www.theplayerstribune.com/posts/kordell-stewart-nfl-football-pittsburgh-steelers'))
    # print(get_tldr('https://getpocket.com/explore/item/the-neuroscience-of-breaking-out-of-negative-thinking-and-how-to-do-it-in-under-30-seconds?utm_source=pocket-newtab'))
    # url = 'https://getpocket.com/explore/item/the-neuroscience-of-breaking-out-of-negative-thinking-and-how-to-do-it-in-under-30-seconds?utm_source=pocket-newtab'
    # article = Article(url)
    # article.download()
    # article.parse()
    # print(article.text)
    summary = get_gpt_summary('https://www.reuters.com/world/china/china-wealth-manager-zhongzhi-flags-insolvency-liabilities-64-bln-2023-11-23/')
    print(summary)
