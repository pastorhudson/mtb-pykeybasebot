from botcommands.covid import get_covid
from botcommands.meh import get_meh
from botcommands.poll_results import get_polls
from botcommands.stardate import get_stardate
from botcommands.till import get_till
import random
import csv
import datetime
import os
import pandas as pd


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


def get_score():
    df = pd.read_csv("./morning_report_score.csv")
    score = df.sum(axis=1, skipna=True)
    return score


def write_score(user):
    score = 0
    file_exists = os.path.isfile('./app/storage/morning_report_score.csv')

    with open('morning_report_score.csv', mode='w') as morningreport_file:
        header = ["User", "Date-time", "Points"]
        score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            score_writer.writerow(header)
        score_writer.writerow([user, datetime.datetime.now(), 10])

    return score


def get_morningreport(user):
    msg = get_obaservation()

    msg += get_stardate()
    msg += get_till(observation=False)
    msg += get_polls()
    msg += get_covid(state="PA", county="Allegheny", observation=False)
    msg += get_covid(state="PA", county="Fayette", observation=False)
    msg += get_meh(observation=False)
    msg += "\n`Daredevil is still blind.`"

    write_score(user)

    return msg


if __name__ == "__main__":
    # print(get_morningreport(user='pastorhudson'))
    print(get_score())