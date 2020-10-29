from botcommands.covid import get_covid
from botcommands.meh import get_meh
from botcommands.poll_results import get_polls
from botcommands.stardate import get_stardate
from botcommands.till import get_till
import random
from botcommands.scorekeeper import write_score, get_score
from pyjokes import pyjokes
from crud import s
from models import Team


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


def get_morningreport(channel):
    team = s.query(Team).filter_by(name=channel).first()
    print(team)
    msg = ["", "", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`"
    msg[0] += get_till(observation=False)
    msg[0] += get_polls(channel) + "\n"
    for local in team.local:
        msg[0] += get_covid(state=local.state, county=local.county, observation=False) + "\n"

    msg[1] += "\nMeh:" + get_meh(observation=False)
    msg[2] += f"\n\nMTB Leaderboard:\n{get_score(channel)}"
    msg[2] += f"\n\nToday's Joke:```{pyjokes.get_joke()}```"

    return msg


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    print(get_morningreport('morethanmarvin,pastorhudson'))
    # print(get_score(channel_members))
