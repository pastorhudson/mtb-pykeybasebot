from prettytable import PrettyTable

from crud import s
from datetime import datetime, timedelta
from models import User, Team, Wager, Bet, Point


def get_team_user(team_name, username):
    team = s.query(Team).filter_by(name=team_name).first()
    user = s.query(User).filter_by(username=username).first()

    return team, user


def get_wagers(team_name):
    team = s.query(Team).filter_by(name=team_name).first()
    wagers = team.get_wagers()
    msg = f"Here's all the current wagers for `{team_name}`\n\n"
    for wager in wagers:
        wager_maker = wager.bets[0].user.username
        x = PrettyTable()
        x.field_names = ["User", "Points", "Position", "Creator"]
        msg += f'Wager: `#{wager.id}` "{wager.description}"\n'
        for bet in wager.bets:
            if bet.user.username == wager_maker:
                x.add_row([bet.user.username, bet.points, bet.position, "*"])
            else:
                x.add_row([bet.user.username, bet.points, bet.position, ""])

        x.align = "r"
        x.sortby = 'Points'
        x.reversesort = True

        msg += f"```{x}\n" \
               f"Default Bet: {wager.points}\n" \
               f'End Time: {wager.et()}````\n'
        msg += "\n\n"
    return msg


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
              f'Default Bet: {wager.points}\n' \
              f'End Time: {wager.et()}```'
        s.close()
        return msg


def make_bet(team_name, username, points, position, wager_id):
    team, user = get_team_user(team_name, username)
    wager = team.get_wager(wager_id)
    if wager and not wager.is_closed:
        if bet := wager.already_bet(user):
            return f"You've already placed a bet that Wager: `#{wager.id}` is `{bet.position}` for `{bet.points}`.\n" \
                   f"This wager will end at {wager.et()}"
        else:
            bet = Bet(points=points, position=True)
            bet.wager = wager
            user.bets.append(bet)
            s.commit()
            msg = f'Wager: `#{wager.id}`\n"{wager.description}"\n' \
                   f'Default Bet: {wager.points}\n' \
                   f'End Time: {wager.et()}'
            s.close()
            return msg

    else:
        return f'Wager: `#{wager.id}` "{wager.description}" is closed for betting.'


def get_bets(username):
    user = s.query(User).filter_by(username=username).first()
    bets = user.get_bets()
    msg = f"Here's all the current wagers for @{username}\n"
    for bet in bets:
        team = s.query(Team).get(bet.wager.team_id)
        msg += f'Wager: `#{bet.wager.id}` "{bet.wager.description}"\n' \
               f'Team: `{team.name}`\n' \
               f'Default Bet: `{bet.wager.points}`\n' \
               f'Your Bet: `{bet.points}`\n' \
               f'Your Position: `{bet.position}`\n' \
               f'End Time: `{bet.wager.et()}`\n' \
               f'Betting Closed: `{bet.wager.is_closed}`\n\n'
    return msg




if __name__ == "__main__":
    # print(make_wager('morethanmarvin,pastorhudson', 'pastorhudson', 'My db is lit', 24, 30))
    # print(get_wagers('morethanmarvin,pastorhudson'))
    # print(make_bet(team_name='morethanmarvin,pastorhudson', username='pastorhudson', points=23, position=True, wager_id=5))
    # print(make_wager(team_name='morethanmarvin,pastorhudson',
    #                  username='pastorhudson',
    #                  description="The moon is flat.",
    #                  points=56,
    #                  position=True,
    #                  minutes=60
    #                  ))
    print(get_bets('pastorhudson'))