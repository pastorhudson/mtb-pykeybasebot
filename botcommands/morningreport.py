from botcommands.covid import get_covid
from botcommands.meh import get_meh
from botcommands.poll_results import get_polls
from botcommands.stardate import get_stardate
from botcommands.till import get_till
import random
from botcommands.scorekeeper import write_score, get_score
import csv
import datetime
import os
import pandas as pd
from botcommands.get_members import get_members


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


# def get_score(channel_members):
#     df = pd.read_csv("./morning_report_score.csv")
#     members = get_members(channel_members)
#     print(members)
#     df.set_index('User', inplace=True)
#
#     df = df.groupby("User", sort=True)["Points"].sum().reset_index()
#     total = df.sort_values(by=['Points', 'User'], ascending=[False, True])
#
#     return total
#
#
# def write_score(user, channel_members):
#     members = get_members(channel_members)
#     score = 0
#
#     file_exists = os.path.isfile('./morning_report_score.csv')
#
#     with open('morning_report_score.csv', mode='a') as morningreport_file:
#         header = ["User", "Date-time", "Points"]
#         score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         if not file_exists:
#             score_writer.writerow(header)
#         score_writer.writerow([user, datetime.datetime.now(), 10])
#
#     return score


def get_morningreport(user, channel_members):

    msg = get_obaservation()
    msg += "`" + get_stardate(observation=False).strip("`") + "`"
    msg += get_till(observation=False)
    msg += get_polls() + "\n"
    msg += get_covid(state="PA", county="Allegheny", observation=False) + "\n"
    msg += get_covid(state="PA", county="Fayette", observation=False) + "\n"

    msg += "Meh:" + get_meh(observation=False)
    msg += "\nDaredevil is still blind."

    # write_score(user, channel_members)

    return msg


if __name__ == "__main__":
    channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}

    print(get_morningreport(user='pastorhudson', channel_members=channel_members))
    print(get_score(channel_members))
