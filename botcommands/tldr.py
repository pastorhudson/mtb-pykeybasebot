from botcommands.scorekeeper import write_score
from smmryAPI.smmryapi import SmmryAPI, SmmryAPIException
import os
from newspaper import Article
from dotenv import load_dotenv
import random
import requests
import re



load_dotenv('../secret.env')


def get_smmry_txt(url, length=4, text=None):
    if url:
        text = get_text(url).text
        if len(text) == 0:
            raise SmmryAPIException

    api_key = os.environ.get('SMMRY_API_KEY')
    payload = {'sm_api_input': text,
               'SM_LENGTH': length,
               'SM_KEYWORD_COUNT': 12}
    surl = f"https://api.smmry.com/&SM_API_KEY={api_key}&SM_LENGTH={length}&SM_KEYWORD_COUNT={payload['SM_KEYWORD_COUNT']}"
    r = requests.post(surl, payload)
    print(r.json())
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
                [f"Here's my tl;dr I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
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
    return tldr


def get_text(url=None):
    article = Article(url)
    article.download()
    article.parse()
    # print(article.title)
    # print(article.top_img)
    # print(article.authors)
    # print(article.movies)
    try:
        article.nlp()
        print(f"Length of Article: {len(article.text)}")

    except Exception as e:
        pass
    return article


async def tldr_react(event, bot, tldr_length):
    if event.msg.sender.username == 'marvn' or event.msg.sender.username == 'morethanmarvin':
        return
    else:
        conversation_id = event.msg.conv_id

        msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
        # pprint(msg.message[0]['msg']['reactions'])
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
                # print(v)
                try:
                    if v['users']['marvn']:
                        reaction_list.append(k)
                except KeyError:
                    pass
        print(reaction_list)
        if ':floppy_disk:' in reaction_list:
            team_name = event.msg.channel.name
            # print("found floppy")
            fail_msg = f"`-10pts` awarded to @{event.msg.sender.username} for spamming :notebook:"
            score = write_score(event.msg.sender.username, 'marvn',
                                team_name, -10, description=fail_msg)
            await bot.chat.send(conversation_id, fail_msg)
            return

        else:
            urls = re.findall(r'(https?://[^\s]+)', original_body)
            if urls:
                print('Found URL')
                tldr_payload = get_tldr(urls[0], tldr_length)

            else:
                print(original_body)
                tldr_payload = get_tldr(length=2, text=original_body, sender=original_sender)

            await bot.chat.react(conversation_id, original_msg_id, ":floppy_disk:")
            try:
                await bot.chat.send(conversation_id, tldr_payload)

            except IndexError as e:
                pass


if __name__ == "__main__":
    pass
    # print(get_tldr('https://www.chicagotribune.   com/coronavirus/ct-nw-hope-hicks-trump-covid-19-20201002-mdjcmul6pnajvg56zoxqrcnf5m-story.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/colin-powell-dies/index.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/joe-biden-democrats-economy-supply-chain-donald-trump-2022-midterms/index.html'))
    # print(len(get_text('https://patch.com/pennsylvania/pittsburgh/consumer-alert-issued-pittsburgh-area-pizza-shop')))
    # print(get_tldr('https://www.gearbest.com/tablet-accessories/pp_009182442856.html?wid=1433363'))
    # print(get_tldr('https://www.theplayerstribune.com/posts/kordell-stewart-nfl-football-pittsburgh-steelers'))
    # print(get_tldr('https://www.cnn.com/videos/politics/2021/10/18/senator-bill-cassidy-republican-donald-trump-2024-ip-ldn-vpx.cnn'))
    # print(get_text('https://www.stltoday.com/news/local/govt-and-politics/parson-issues-legal-threat-against-post-dispatch-after-database-flaws-exposed/article_93f4d7d6-f792-5b1b-b556-00b5cac23af3.html?utm_medium=social&utm_source=twitter&utm_campaign=user-share'))