from botcommands.meh import get_meh
from botcommands.stardate import get_stardate
from botcommands.till import get_till
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


def get_morningreport(channel):
    team = s.query(Team).filter_by(name=channel).first()

    msg = ["", "", "", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`\n"
    # msg[0] += get_poll_result(channel)
    # for place in team.location.all():
    #     msg[0] += get_covid(state=place.state, county=place.county, observation=False) + "\n"

    # msg[0] += get_vaccine_data()
    msg[1] += "\nMeh:" + get_meh(observation=False)
    msg[2] += f"\n\n{get_score(channel)}"
    msg[2] += get_till(team_name=team.name, observation=False)
    msg[3] += f"Today's Joke:```{get_joke(False)}```"
    s.close()
    return msg


# async def send_report(event):
#
#
#     if event.msg.content.type_name == "text":
#         team_name = event.msg.channel.name
#         if str(event.msg.content.text.body).startswith("!"):
#             score = write_score('@marvn', event.msg.sender.username, team_name, 3, description='sent msg')
#         else:
#             logging.info(f'Giving {event.msg.sender.username} {len(str(event.msg.content.text.body))}pts')
#             score = write_score('@marvn', event.msg.sender.username, team_name, len(str(event.msg.content.text.body)), description='msg')
#     if event.msg.content.type_name == 'reaction' and event.msg.sender.username != '@marvn':
#         team_name = event.msg.channel.name
#         logging.info(f'Giving {event.msg.sender.username} 4 pts')
#         score = write_score('@marvn', event.msg.sender.username, team_name, 4, description='react')
#     pass


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    get_morningreport('morethanmarvin,pastorhudson')
    # print(get_score(channel_members))
