from smmryAPI.smmryapi import SmmryAPI
import os
from dotenv import load_dotenv


load_dotenv('../secret.env')


def get_tldr(url):
    tldr = ""

    smmry = SmmryAPI(os.environ.get('SMMRY_API_KEY'))
    s = smmry.summarize(url, sm_length=3, sm_keyword_count=12)
    tldr = "\n".join([f"Here's my tl;dr I could only reduce it by {s.sm_api_content_reduced}.\nI'm sorry I'm such a failure.", "```",
                      str(s), "```"])
    return tldr


if __name__ == "__main__":
    print(get_tldr('https://www.npr.org/2020/10/01/919283793/texas-governor-limits-ballot-drop-off-locations-local-officials-vow-to-fight-bac'))
