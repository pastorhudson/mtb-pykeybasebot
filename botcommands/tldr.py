from smmryAPI.smmryapi import SmmryAPI
import os
from dotenv import load_dotenv


load_dotenv('../secret.env')


def get_tldr(url):
    tldr = ""

    smmry = SmmryAPI(os.environ.get('SMMRY_API_KEY'))
    s = smmry.summarize(url, sm_length=3, sm_keyword_count=12)
    tldr = "\n".join([f'This is the best tl;dr I could make, original reduced by {s.sm_api_content_reduced}', "```",
                      str(s), "```"])
    return tldr


if __name__ == "__main__":
    print(get_tldr('https://www.npr.org/2020/10/01/919283793/texas-governor-limits-ballot-drop-off-locations-local-officials-vow-to-fight-bac'))
