from smmryAPI.smmryapi import SmmryAPI, SmmryAPIException
import os
from newspaper import Article
from dotenv import load_dotenv
import random
import requests


load_dotenv('../secret.env')


def get_smmry_txt(url):
    txt = get_text(url)
    if len(txt) == 0:
        raise SmmryAPIException
    api_key = os.environ.get('SMMRY_API_KEY')
    payload = {'sm_api_input': get_text(url),
               'sm_length': 3,
               'sm_keyword_count': 12}
    surl = f"https://api.smmry.com/&SM_API_KEY={api_key}"
    r = requests.post(surl, payload)
    print(r.json())
    if "TEXT IS TOO SHORT" in r.json()['sm_api_message']:
        if len(txt) > 0:
            return {f'sm_api_content_reduced': f'Zero Percent because it was only {len(txt)} char',
                        'sm_api_content': txt}
    return r.json()


def get_tldr(url):
    tldr = ""
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I hope this makes you happy because I'm not.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
    try:
        s = get_smmry_txt(url)
        tldr = "\n".join(
            [f"Here's my tl;dr I could only reduce it by {s['sm_api_content_reduced']}.\n{random.choice(observations)}",
             "```",
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
    try:
        article.nlp()
        print(f"Length of Article: {len(article.text)}")


    except Exception as e:
        import nltk
        nltk.download('punkt')
        article.nlp()
    return article.text


if __name__ == "__main__":
    pass
    # print(get_tldr('https://www.chicagotribune.   com/coronavirus/ct-nw-hope-hicks-trump-covid-19-20201002-mdjcmul6pnajvg56zoxqrcnf5m-story.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/colin-powell-dies/index.html'))
    # print(get_tldr('https://www.cnn.com/2021/10/18/politics/joe-biden-democrats-economy-supply-chain-donald-trump-2022-midterms/index.html'))
    # print(len(get_text('https://patch.com/pennsylvania/pittsburgh/consumer-alert-issued-pittsburgh-area-pizza-shop')))
    # print(get_tldr('https://www.gearbest.com/tablet-accessories/pp_009182442856.html?wid=1433363'))
    print(get_tldr('https://www.theplayerstribune.com/posts/kordell-stewart-nfl-football-pittsburgh-steelers'))
    # print(get_tldr('https://www.cnn.com/videos/politics/2021/10/18/senator-bill-cassidy-republican-donald-trump-2024-ip-ldn-vpx.cnn'))