import datetime
import pandas as pd
import os
import csv
from crud import s
from models import User, Team


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_score(channel_members, channel):
    df = pd.read_csv(f"./storage/{channel}.csv")
    members = channel_members
    df.set_index('User', inplace=True)

    df = df.groupby("User", sort=True)["Points"].sum().reset_index()
    total = df.sort_values(by=['Points', 'User'], ascending=[False, True])
    total_members = total[total.User.isin(members)]
    msg = "```" + total_members.to_string(index=False) + "```"

    return msg


def make_wager(user, channel_members, channel, wager):
    msg = ""
    if RepresentsInt(wager.split(" ")[0]):
        points_bet = wager.split(" ")[0]
        print(len(points_bet))
        msg = f"@{user} Has wagered `{points_bet}` points \n\n```{wager[3:]}```"
        msg += "\nVote Against: :no_entry_sign:\n" \
               "Vote For: :white_check_mark:"
        return msg
    else:
        return "I didn't get a wager in the proper format\n" \
               "Usage: <points> <Wager Description>\n" \
               '!wager 25 Daredevil is Blind'


def has_points():

    return True


def get_users():
    t = Team(name='morethanbits')
    u = User(username='marvn')
    t.users = [u]
    s.add(t)
    s.add(u)
    s.commit()
    print(u.teams)
    #
    users_list = s.query(User.username).all()
    for u in users_list:
        print(u.username)

    # print(users)
    s.close()


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}, {'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    # channel = "morethanbits"
    # wager = "25 Amy Coney Barrette will be confirmed tonight"
    # print(make_wager("pastorhudson", channel_members, channel, wager))
    get_users()
