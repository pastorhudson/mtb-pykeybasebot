from botcommands.meh import get_meh
from botcommands.stardate import get_stardate
from botcommands.till import get_till
from botcommands.school_closings import get_school_closings
import random
from botcommands.scorekeeper import write_score, get_score
# from pyjokes import pyjokes
from botcommands.jokes import get_joke
from crud import s
from models import Team
import logging

from botcommands.scorekeeper import write_score

logging.basicConfig(level=logging.DEBUG)


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


async def get_morningreport(channel):
    schools = ["Albert Gallatin", "Uniontown", "North Hills"]
    closings = get_school_closings(schools)
    team = s.query(Team).filter_by(name=channel).first()

    msg = ["", "", "", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`\n"

    # msg[0] += get_poll_result(channel)
    # for place in team.location.all():
    #     msg[0] += get_covid(state=place.state, county=place.county, observation=False) + "\n"
    meh = await get_meh(observation=False)
    msg[1] += "\nMeh:" + meh
    msg[2] += f"\n\n{get_score(channel)}"
    msg[2] += get_till(team_name=team.name, observation=False)
    msg[3] += f"Today's Joke:```{get_joke(False)}"
    msg[4] += f"```"
    s.close()
    return msg


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    get_morningreport('morethanmarvin,pastorhudson')
    # print(get_score(channel_members))
