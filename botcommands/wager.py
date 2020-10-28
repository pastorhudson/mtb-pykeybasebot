from prettytable import PrettyTable
from prettytable.prettytable import MSWORD_FRIENDLY

from crud import s
from datetime import datetime, timedelta
from models import User, Team, Wager, Bet, Point


def get_team_user(team_name, username):
    team = s.query(Team).filter_by(name=team_name).first()
    user = s.query(User).filter_by(username=username).first()

    return team, user


def get_wagers(team_name):
    team = s.query(Team).filter_by(name=team_name).first()
    try:
        wagers = team.wagers
        msg = f"Here's all the current wagers for `{team_name}`\n\n"
        for wager in wagers:
            msg += f'Wager: `#{wager.id}` "{wager.description}"\n'
            msg += get_wager_bets(wager)
        return msg
    except AttributeError:
        return "Something went wrong. Clearly your fault."



def make_wager(team_name, username, description, points, position,  minutes):
    if points < 0:
        return f"`{points}` is a negative number. All wagers must be positive integers.\n" \
               f"Usage: `!wager <points> <Description>`\n" \
               f"If you'd like to bet something will not happen reflect that in the description."

    team, user = get_team_user(team_name, username)

    existing_wager = team.wager_exists(description)
    exists = False
    for w in existing_wager:
        if w.description == description:
            exists = True
            return f"Wager: `#{w.id}` {w.description} already exists.\n" \
                   f"```Usage: !bet <#wager> <points> <True/False>```"

    if not exists:
        end_time = datetime.now() + timedelta(minutes=minutes)
        bet = Bet(points=points, position=position)
        wager = Wager(team_id=team.id, description=description, points=points, start_time=datetime.now(), end_time=end_time)
        bet.wager = wager
        user.bets.append(bet)
        s.commit()
        msg = f'Wager: `#{wager.id}`\n"{wager.description}"\n```' \
              # f'End Time: {wager.et()}```'
        s.close()
        return msg


def make_bet(team_name, username, points, position, wager_id):
    team, user = get_team_user(team_name, username)
    wager = s.query(Wager).get(wager_id)
    print(wager)
    msg = ""
    if wager:
        if wager.team_id != team.id:
            return f'This team is not able to access wager `#{wager.id}`.'
        if wager.is_closed:
            return f'Wager: `#{wager.id}` "{wager.description}" is closed for betting.'

        if bet := wager.already_bet(user):
            print(bet)
            return f"You've already bet `{bet.points}` points wager `#{wager.id}` is `{bet.position}`.\n" \
                   f"Wager `#{wager.id}`: {wager.description}\n" \
                   f"This wager will end at {wager.et()}\n" \
                   f"{get_wager_bets(wager)}"
        else:
            bet = Bet(points=points, position=position)
            bet.wager = wager
            bet.user = user
            s.add(bet)
            s.commit()
            msg += f'Your bet has been recorded.\n' \
                   f'Wager: `#{wager.id}` "{wager.description}"\n'
            msg += get_wager_bets(wager)
            s.close()
            return msg

    else:
        return f"The immense scale of your failure is stunning, but not surprising.\n" \
               f"There isn't a wager `#{wager_id}`."


def get_bets(username):
    user = s.query(User).filter_by(username=username).first()
    bets = user.bets
    msg = f"Here's all the current wagers for @{username}\n"
    bet_table = PrettyTable()
    bet_table.border = False
    bet_table.field_names = ["#", "Pts", "Pos", "Win"]

    for bet in bets:
        bet_table.add_row([bet.wager.id, bet.points, bet.position, bet.result])
    bet_table.align = "r"
    bet_table.sortby = '#'
    # bet_table.reversesort = True
    msg = f"```" \
          f"{bet_table}" \
          f"```"

    return msg


def get_wager_bets(wager):
    """Gests all the associated bets for a given wager object, returns a pretty table"""
    x = PrettyTable()
    x.set_style(MSWORD_FRIENDLY)
    x.border = False
    wager_maker = wager.bets[0].user.username
    x.field_names = ["User", "Pts", "Pos"]

    msg = ""
    for bet in wager.bets:
        if bet.user.username == wager_maker:
            x.add_row([f"{bet.user.username}*", bet.points, bet.position])
        else:
            x.add_row([bet.user.username, bet.points, bet.position])

    x.align = "r"
    x.sortby = 'Pts'
    x.reversesort = True

    msg += f"```{x}\n```\n\n" \
           # f'End Time: {wager.et()}```'

    return msg


if __name__ == "__main__":
    # print(make_wager('morethanmarvin,pastorhudson', 'morethanmarvin', 'I am the best bot.', 100, True, 30))
    print(get_wagers('someteam'))
    # print(make_bet(team_name='morethanmarvin,pastorhudson', username='pastorhudson', points=23, position=True, wager_id=6))
    # print(make_wager(team_name='morethanmarvin,pastorhudson',
    #                  username='pastorhudson',
    #                  description="The moon is flat.",
    #                  points=56,
    #                  position=True,
    #                  minutes=60
    #                  ))
    # print(get_bets('pastorhudson'))