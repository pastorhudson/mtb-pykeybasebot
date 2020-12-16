from botcommands.covid import get_covid
from botcommands.meh import get_meh
from botcommands.poll_results import get_poll_result
from botcommands.stardate import get_stardate
from botcommands.till import get_till
import random
from botcommands.scorekeeper import write_score, get_score
# from pyjokes import pyjokes
from botcommands.jokes import get_joke
from crud import s
from models import Team
from botcommands.update_vaccine import get_vaccine_data


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


def get_morningreport(channel):
    team = s.query(Team).filter_by(name=channel).first()

    msg = ["", "", "", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`\n"
    # msg[0] += get_poll_result(channel)
    for place in team.location.all():
        msg[0] += get_covid(state=place.state, county=place.county, observation=False) + "\n"

    msg[0] += get_vaccine_data()
    msg[1] += "\nMeh:" + get_meh(observation=False)
    msg[2] += f"\n\n{get_score(channel)}"
    msg[2] += get_till(team_name=team.name, observation=False)
    msg[3] += f"Today's Joke:```{get_joke(False)}```"
    s.close()
    return msg


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    get_morningreport('morethanmarvin,pastorhudson')
    # print(get_score(channel_members))
