from prettytable import PrettyTable
from crud import s
from datetime import datetime, timezone
from models import Since
from botcommands.utils import get_team
import pytz
import dateparser


def get_observation():
    observations = [
        'Seems like yesterday.\n',
        'Counting the days.\n'
    ]
    return observations[0]


def get_since(team_name, observation=True):
    x = PrettyTable()
    x.field_names = ["Event", "since", ]
    team = get_team(team_name)
    current_time = datetime.now(timezone.utc)
    sinces = team.sinces.filter(Since.event < current_time).all()

    msg = ""
    if observation:
        msg += get_observation()
    msg += "It's been:\n"
    for since in sinces:
        msg += f"""{since}\n"""

    return msg


def set_since(team_name, event_name, event_time):
    event_name = event_name.strip('`').strip()
    team = get_team(team_name)
    since_event = dateparser.parse(event_time, settings={'PREFER_DATES_FROM': 'past',
                                                        'TIMEZONE': 'US/Eastern',
                                                        'RETURN_AS_TIMEZONE_AWARE': True
                                                        })
    if since_event is None:
        return None

    current_time = datetime.now(pytz.timezone('America/New_York'))
    sinces = team.sinces.filter(Since.name == event_name).filter(Since.event < current_time).all()
    if len(sinces) > 0:
        return f"There is already a since set for {event_name}\n{sinces[0]}"
    try:
        since = Since(team_id=team.id, name=event_name, event=since_event)
        s.add(since)
        s.commit()
    except TypeError as e:
        return None
    return f"{since}"


def reset_since(team_name, since_id):
    numerical_since_id = int(since_id.strip('#'))
    team = get_team(team_name)
    current_time = datetime.now(timezone.utc)
    try:
        since_to_reset = team.sinces.filter(Since.id == numerical_since_id).one()
        if since_to_reset:
            since_to_reset.event = current_time
            s.add(since_to_reset)
            s.commit()
        else:
            print('Not your since')
        return since_to_reset
    except Exception as e:
        print(e)
        return "Fail"


if __name__ == "__main__":
    print(get_since(team_name='marvn,pastorhudson'))
    print(reset_since("marvn,pastorhudson", since_id='#3'))
    # print(get_since(team_name='marvn,pastorhudson', since_id="#1"))
    # print('TEST')
    # team = get_team('marvn,pastorhudson')
    # print(team)
    # print(set_since(team_name='marvn,pastorhudson', event_name='Christmas', event_time='8:30 AM on December 25'))
    # print('DONE')
    # print(set_since(team_name='morethanmarvin,pastorhudson', event_name='US Presidential Election', event_time='November 3 2024'))
    # print(set_since(team_name='morethanmarvin,pastorhudson', event_name='TESTTESTTEST', event_time='5pm'))


