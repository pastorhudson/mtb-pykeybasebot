from botcommands.meh import get_meh
from botcommands.since import get_since
from botcommands.stardate import get_stardate
from botcommands.till import get_till
from botcommands.school_closings import get_school_closings
import random
# from botcommands.scorekeeper import get_score
from botcommands.jokes import get_joke
import logging
from crud import s
from models import Team
from botcommands.news import get_top_hacker_news
from botcommands.weather import get_weather

logging.basicConfig(level=logging.DEBUG)


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


async def get_morningreport(channel):
    schools = ['uniontown', 'albert', 'north hills']

    team = s.query(Team).filter_by(name=channel).first()

    msg = ["", "", "", "", "\n\n\n\nToday's Closings: ```Normal Schedule```\n", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`\n\n"

    meh = await get_meh(observation=False)
    msg[1] = "\nMeh:" + meh
    msg[2] = f"\n\nEverything is made up and the points don't matter.\n\n"
    msg[2] += get_till(team_name=team.name, observation=False)
    msg[2] += get_since(team_name=team.name, observation=False)
    msg[2] += "\n\nToday's Top Hacker News:\n"
    msg[2] += get_top_hacker_news()
    msg[3] += f"\nToday's Joke:```{get_joke(False)}```"
    closings, no_school = get_school_closings(search=schools, observations=False)
    if no_school:
        msg[4] = closings['msg']
    msg[5] = get_weather("Uniontown", (39.90008, -79.71643))
    s.close()
    return msg


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    get_morningreport('morethanmarvin,pastorhudson')

    # print(get_score(channel_members))
