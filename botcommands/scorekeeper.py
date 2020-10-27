# from botcommands.get_members import get_members
import datetime
import pandas as pd
import os
import csv
from crud import s
from models import Point, Team, User


def get_score(channel_members, channel):
    df = pd.read_csv(f"./storage/{channel}.csv")
    members = channel_members
    df.set_index('User', inplace=True)

    df = df.groupby("User", sort=True)["Points"].sum().reset_index()
    total = df.sort_values(by=['Points', 'User'], ascending=[False, True])
    total_members = total[total.User.isin(members)]
    msg = "```" + total_members.to_string(index=False) + "```"

    return msg


def write_score(user, channel_members, sender, channel, team_name, points=10):
    file_exists = os.path.isfile(f'./storage/{channel}.csv')
    if not file_exists:
        with open(f'./storage/{channel}.csv', mode='w') as morningreport_file:
            header = ["User", "Date-time", "Points", "Sender", "Conv_id"]
            score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                score_writer.writerow(header)

    with open(f'./storage/{channel}.csv', mode='a') as morningreport_file:
        score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        score_writer.writerow([user, datetime.datetime.now(), points, sender, channel])
        team = s.query(Team).filter(Team.name.match(team_name)).first()
        giver = s.query(User).filter(User.username.match(sender)).first()
        receiver = s.query(User).filter(User.username.match(user)).first()

        points = Point(giver=giver, points=points, receiver=receiver, team_id=team.id)
        s.add(points)
        s.commit()
        s.close()

    return


if __name__ == "__main__":
    channel_members = {'owners': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}, {'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    print(get_score(channel_members))
