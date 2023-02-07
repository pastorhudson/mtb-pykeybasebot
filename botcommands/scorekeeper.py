import datetime
import os
import csv

from crud import s
from models import Point, Team, User
from prettytable import PrettyTable


def get_score(channel_name, year=datetime.datetime.utcnow().year):
    x = PrettyTable(reversesort=True)
    x.field_names = ["Achiever", "Score",]
    team = s.query(Team).filter_by(name=channel_name).first()
    msg = f"```{team.name} {year}\n-- Leaderboard --\n"
    for k, v in team.get_score(year=year).items():
        x.add_row([k.username, v])
    x.align = "r"
    x.padding_width = 2
    x.sortby = "Score"

    msg += f"{x}"

    msg += f"\n-- Generosity --\n"
    y = PrettyTable(reversesort=True)
    y.field_names = ["Achiever", "Score", ]
    for k, v in team.get_most_generous(year=year).items():
        y.add_row([k.username, v])
    y.align = "r"
    y.padding_width = 2
    y.sortby = "Score"

    msg += f"{y}"

    msg += f"\n-- Leading Person of the Year --\n"
    y = PrettyTable(reversesort=True)
    y.field_names = ["Achiever", "Score", ]
    for k, v in team.get_leading_person(year=year).items():
        y.add_row([k.username, v])
    y.align = "r"
    y.padding_width = 2
    y.sortby = "Score"

    msg += f"{y}"

    return msg


def write_score(user, sender, team_name, points, description):
    # file_exists = os.path.isfile(f'./storage/{channel}.csv')
    # if not file_exists:
    #     with open(f'./storage/{channel}.csv', mode='w') as morningreport_file:
    #         header = ["User", "Date-time", "Points", "Sender", "Conv_id"]
    #         score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #         if not file_exists:
    #             score_writer.writerow(header)
    #
    # with open(f'./storage/{channel}.csv', mode='a') as morningreport_file:
    #     score_writer = csv.writer(morningreport_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     score_writer.writerow([user, datetime.datetime.now(), points, sender, channel])
    team = s.query(Team).filter(Team.name.match(team_name)).first()
    giver = s.query(User).filter(User.username.match(sender)).first()
    receiver = s.query(User).filter(User.username.match(user)).first()

    points = Point(giver_id=giver.id, receiver_id=receiver.id, team_id=team.id, points=points, description=description)
    s.add(points)
    s.commit()
    s.close()

    return


def sync_score(channel):
    with open(f'./storage/{channel.replace(",", "")}.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team = s.query(Team).filter(Team.name.match(channel)).first()
            receiver = s.query(User).filter(User.username.match(row['User'])).first()
            giver = s.query(User).filter(User.username.match(row['Sender'])).first()

            points = Point(giver_id=giver.id, receiver_id=receiver.id, team_id=team.id, points=int(row['Points']))
            s.add(points)
            s.commit()
            s.close()
            print(row)


if __name__ == "__main__":
    pass
    # channel_members = {'owners': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}, {'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    #
    # print(get_score(channel_members))
    # team = s.query(Team).filter_by(name='morethanmarvin,pastorhudson').first()
    # for p in team.points:
        # print(f"{p.point_giver} gave {p.point_receiver} {p.points} points.")
        # pass
    # s.close()
    # u = s.query(User).filter_by(username='pastorhudson').first()
    # print(u)
    # scores = (
    #     s.query(User.username, func.count(User.points_received).label("count")).order_by(desc("count"))
    # ).all()
    # print(scores)
