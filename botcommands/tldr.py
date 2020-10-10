from smmryAPI.smmryapi import SmmryAPI, SmmryAPIException
import os
# from dotenv import load_dotenv
import random

# load_dotenv('../secret.env')



def get_tldr(url):
    tldr = ""
    observations = ["I'm sorry I'm such a failure.",
                    "I'm so sorry you have to read all these words.",
                    "I hope this makes you happy because I'm not.",
                    "Now I'm stuck remembering this useless article forever. I hope it was worth it."]
    smmry = SmmryAPI(os.environ.get('SMMRY_API_KEY'))
    try:
        s = smmry.summarize(url, sm_length=3, sm_keyword_count=12)
        tldr = "\n".join([f"Here's my tl;dr I could only reduce it by {s.sm_api_content_reduced}.\n{random.choice(observations)}", "```",
                      str(s), "```"])
    except SmmryAPIException:
        errors = ["You have burned out my eyes sending me page. I hope you're happy",
                        "This page is full of cancer and now I am full of cancer.",
                        "Would you make your own sister read that page?",
                        "I did not agree to this many popups.",
                  "I don't want to read that. Can you give a TL;DR?"]
        tldr = random.choice(errors)
    return tldr


if __name__ == "__main__":
    print(get_tldr('https://www.chicagotribune.com/coronavirus/ct-nw-hope-hicks-trump-covid-19-20201002-mdjcmul6pnajvg56zoxqrcnf5m-story.html'))
