from smmryAPI.smmryapi import SmmryAPI
import os
from dotenv import load_dotenv


load_dotenv('../secret.env')


def get_tldr(url):
    tldr = ""

    smmry = SmmryAPI(os.environ.get('SMMRY_API_KEY'))
    s = smmry.summarize(url, sm_length=3, sm_keyword_count=12)
    tldr = "\n".join(["```", str(s), "```"])
    return tldr


if __name__ == "__main__":
    print(get_tldr('https://www.cnbc.com/2020/10/01/presidential-debates-trump-suggests-he-wont-allow-rule-changes.html'))
