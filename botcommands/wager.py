from prettytable import PrettyTable
from prettytable.prettytable import MSWORD_FRIENDLY

from crud import s
from datetime import datetime, timedelta
from models import User, Team, Wager, Bet, Point
import pykeybasebot.types.chat1 as chat1
from botcommands.utils import get_team_user


async def update_wager_msg(bot, wager, msg):

    for message in wager.messages.all():
        await bot.chat.edit(message.conv_id, int(message.msg_id), msg)


async def payout_wager(username, team_name, wager_id, result, bot):
    team, user = get_team_user(team_name, username)
    marvn = s.query(User).filter_by(username='marvn').first()
    if result.lower() == 'true':
        result = True
    else:
        result = False
    msg = ""
    for wager in team.wagers:
        if wager.id == wager_id:

            msg = f"Wager: `#{wager.id}` - `CLOSED`\n" \
                  f'"{wager.description}"\n' \
                  f"{get_wager_bets(wager)}" \
                  f"Result: `{result}`"
            wager.result = result
            payout = False
            for bet in wager.bets[1:]:
                if bet.position != wager.bets[0].position:
                    payout = True
            if payout:
                for bet in wager.bets:
                    bet.result = result
                    if bet.position is not result:
                        points = bet.points * -1
                        msg += f"\nDeducting {bet.points} points from {bet.user}"
                        p = Point(giver_id=marvn.id, receiver_id=bet.user.id, team_id=team.id, points=points, description=f"Wager: #{wager.id}")

                        s.add(p)
                    else:
                        msg += f"\nPaying {bet.points} points to {bet.user}"
                        p = Point(giver_id=marvn.id, receiver_id=bet.user.id, team_id=team.id, points=bet.points, description=f"Wager: #{wager.id}")
                        s.add(p)
                    wager.is_closed = True
                    s.commit()
                await update_wager_msg(bot, wager, msg)
                s.close()
                return msg
            else:
                msg = f"Nobody took the Wager `#{wager_id}` so this didn't payout.\n" \
                       f"`{wager.description}`"
                wager.is_closed = True

                s.commit()
                await update_wager_msg(bot, wager, msg)
                s.close()
                return msg

    return f"Wager `#{wager_id}` is either already closed or non-existant."


#  Moved to utils.py
# def get_team_user(team_name, username):
#     team = s.query(Team).filter_by(name=team_name).first()
#     user = s.query(User).filter_by(username=username).first()
#     # s.close()
#
#     return team, user


def get_wagers(team_name):
    team = s.query(Team).filter_by(name=team_name).first()
    wager_msgs = {}
    try:
        wagers = team.wagers
        print(wagers)
        # msg = f"Here's all the current wagers for `{team_name}`\n\n"
        for wager in wagers:
            msg = ""
            if not wager.is_closed:
                msg += f'Wager: `#{wager.id}`\n' \
                       f'"{wager.description}"\n'
                msg += get_wager_bets(wager)
                wager_msgs[f'{wager.id}'] = msg
        s.close()
        return wager_msgs
    except AttributeError:
        return "Something went wrong. Clearly your fault."


def make_wager(team_name, username, description, points, position,  minutes):
    if 1 > points:
        return f"`{points}` is a terrible failure. All wagers must be positive integers.\n" \
               f"Usage: `!wager <points> <Description>`\n" \
               f"If you'd like to bet something will not happen reflect that in the description."
    if points > 5001:
        return f"`{points}` is a terrible failure. All wagers must be positive integers less than 5001.\n" \
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
        msg = f'Wager: `#{wager.id}`\n"{wager.description}"\n' \
              f'{get_wager_bets(wager)}'
        s.close()
        payload = {"msg": msg, "wager_id": wager.id}
        return payload


def make_bet(team_name, username, points, position, wager_id):
    if points < 1:
        return "You can't bet negative points."
    if points > 5000:
        return "5000 is the max bet."
    team, user = get_team_user(team_name, username)

    wager = s.query(Wager).get(wager_id)
    msg = ""
    if wager:
        if wager.team_id != team.id:
            return f'This team is not able to access wager `#{wager.id}`.'
        if wager.is_closed:
            return f'Wager: `#{wager.id}` "{wager.description}" is closed for betting.'

        if bet := wager.already_bet(user):
            print(bet)
            return f"Wager `#{wager.id}`: {wager.description}\n" \
                   f"{get_wager_bets(wager)}" \
                   # f"\n\n{user.username} already wagered `{bet.points}` `#{wager.id}` will be `{bet.position}`.\n"
        if points > wager.bets[0].points:
            return f"You can't bet more than {wager.bets[0].points} on wager `#{wager.id}`"
        else:
            bet = Bet(points=points, position=position)
            bet.wager = wager
            bet.user = user
            s.add(bet)
            s.commit()
            msg += f'Wager: `#{wager.id}` "{wager.description}"\n'
            msg += get_wager_bets(wager)
            # msg += f'\n@{user.username} your bet has been recorded.\n'
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
    s.close()
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

    msg += f"```{x}```" \
           # f'End Time: {wager.et()}```'
    return msg


if __name__ == "__main__":
    msg_id = chat1.MessageID
    print(msg_id)
    pass
    # print(make_wager('morethanmarvin,pastorhudson', 'morethanmarvin', 'I am the best bot.', 100, True, 30))
    # print(get_wagers('someteam'))
    # print(make_bet(team_name='morethanmarvin,pastorhudson', username='pastorhudson', points=23, position=True, wager_id=6))
    # print(make_wager(team_name='morethanmarvin,pastorhudson',
    #                  username='pastorhudson',
    #                  description="The moon is flat.",
    #                  points=56,
    #                  position=True,
    #                  minutes=60
    #                  ))
    # print(get_bets('pastorhudson'))
    # print(payout_wager('pastorhudson', "morethanmarvin,pastorhudson", 7, True))
