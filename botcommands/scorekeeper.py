# from botcommands.get_members import get_members
import datetime
import pandas as pd
import os
import csv


def get_score(channel_members):
    df = pd.read_csv("./storage/score.csv")
    members = channel_members
    df.set_index('User', inplace=True)

    df = df.groupby("User", sort=True)["Points"].sum().reset_index()
    total = df.sort_values(by=['Points', 'User'], ascending=[False, True])
    total_members = total[total.User.isin(members)]
    msg = "```" + total_members.to_string(index=False) + "```"

    return msg


def write_score(user, channel_members, sender, channel, points=10):
    file_exists = os.path.isfile('./storage/score.csv')
    if not file_exists:
        with open('./storage/score.csv', mode='w') as morningreport_file:
            header = ["User", "Date-time", "Points", "Sender", "Conv_id"]
            score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                score_writer.writerow(header)

    with open('./storage/score.csv', mode='a') as morningreport_file:
        score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        score_writer.writerow([user, datetime.datetime.now(), points, sender, channel])

    score = get_score(channel_members)

    return score


if __name__ == "__main__":
    channel_members = {'owners': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}, {'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    print(get_score(channel_members))
