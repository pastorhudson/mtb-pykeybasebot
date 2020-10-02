from smmryAPI.smmryapi import SmmryAPI
import os
from dotenv import load_dotenv
import random

load_dotenv('../secret.env')



def get_tldr(url):
    tldr = ""
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I didn't even read the tl;dr.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
    smmry = SmmryAPI(os.environ.get('SMMRY_API_KEY'))
    s = smmry.summarize(url, sm_length=3, sm_keyword_count=12)
    tldr = "\n".join([f"Here's my tl;dr I could only reduce it by {s.sm_api_content_reduced}.\n{random.choice(observations)}", "```",
                      str(s), "```"])
    return tldr


if __name__ == "__main__":
    print(get_tldr('https://www.npr.org/2020/10/01/919283793/texas-governor-limits-ballot-drop-off-locations-local-officials-vow-to-fight-bac'))
