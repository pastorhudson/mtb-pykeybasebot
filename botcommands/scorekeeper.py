import datetime
import logging
import os
import csv

from botcommands.sync import sync, get_channel_members
from crud import s
from models import Point, Team, User
from prettytable import PrettyTable
from string import punctuation
from pykeybasebot.utils import get_channel_members



logging.basicConfig(level=logging.DEBUG)



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

    msg += f"\n-- Leading Person of the the Year --\n"
    y = PrettyTable(reversesort=True)
    y.field_names = ["Achiever", "Score", ]
    for k, v in team.get_leading_person(year=year).items():
        y.add_row([k.username, v])
    y.align = "r"
    y.padding_width = 2
    y.sortby = "Score"

    msg += f"{y}```"

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

def RepresentsInt(s):
    try:
        int(s)
        return True
    except Exception as e:
        return False


async def award(bot, event, sender, recipient, team_members, points, description):

    pts_max = 5000

    instructions = f"You have failed. I'm not surprised.\n" \
                   f"```You can only give points to someone in this chat.\n" \
                   f"You can't give more than {pts_max} points at a time.\n" \
                   f"You can't give negative points.\n" \
                   f"Points must be whole numbers.\n" \
                   f"No cutesy extra characters, or I'll deduct from your score.\n" \
                   f"You can't give points to yourself.```\n" \
                   f"Usage: `!award <@user> <points> <description>`"

    conversation_id = event.msg.conv_id
    user = event.msg.sender.username
    team_name = event.msg.channel.name
    message_id = event.msg.id


    if not recipient:
        recipient = event.msg.at_mention_usernames[0]

    try:

        if not points:
            return instructions

        if points < 0 and sender != 'pastorhudson':
            logging.info("Points are Negative!")
            user = event.msg.sender.username
            return f"`-500` points awarded to @{user} for trying to be negative. You're not allowed to give negative points."

        if user in team_members:
            logging.info("User is in members")
        if recipient == event.msg.sender.username:
            logging.info(f"{event.msg.sender.username} is {user}")
            return f"@{user} you can't give points to yourself. How incredibly sad."
        if points > pts_max:
            logging.info(f"{points} is greater than {pts_max}")
            return f"@{user} you can't give more than {pts_max} points at a time. I know you know that. You know that I know that you know that."
        if recipient in team_members and recipient != event.msg.sender.username and points <= pts_max:
            score = write_score(recipient, event.msg.sender.username, team_name, points, description=description)
            await bot.chat.react(conversation_id, message_id, ":marvin:")
            return f"Awarded {points} points to @{recipient}."
        else:
            return instructions
    except Exception as e:
        write_score('marvn', event.msg.sender.username, team_name, -42, description=description)
        return (f"You did it wrong.\n `-42` points deducted from  "
                f"@{event.msg.sender.username} for trying to be cute.\n{instructions}")



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
