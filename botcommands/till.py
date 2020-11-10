from prettytable import PrettyTable
from crud import s
from datetime import datetime, timezone
from models import Till
from botcommands.utils import get_team
import dateparser


def get_observation():
    observations = [
        'The end is coming.\n',
        'Counting the days.\n'
    ]
    return observations[0]


def get_till(team_name, observation=True):
    x = PrettyTable()
    x.field_names = ["Event", "Till", ]
    team = get_team(team_name)
    current_time = datetime.now(timezone.utc)
    tills = team.tills.filter(Till.event > current_time).all()

    msg = ""
    if observation:
        msg += get_observation()
    msg += "There are:\n"
    for till in tills:
        msg += f"{till}\n"

    return msg


def set_till(team_name, event_name, event_time):
    team = get_team(team_name)
    till_event = dateparser.parse(event_time, settings={'PREFER_DATES_FROM': 'future'})
    current_time = datetime.now(timezone.utc)
    tills = team.tills.filter(Till.name == event_name).filter(Till.event > current_time).all()
    if len(tills) > 0:
        return f"There is already a till set for {event_name}\n{tills[0]}"
    till = Till(team_id=team.id, name=event_name, event=till_event)
    s.add(till)
    s.commit()
    return f"{till}"


if __name__ == "__main__":
    print(get_till(team_name='morethanmarvin,pastorhudson'))
    # print(set_till(team_name='morethanmarvin,pastorhudson', event_name='Yule', event_time='8:30 AM on Monday, December 21'))
    # print(set_till(team_name='morethanmarvin,pastorhudson', event_name='US Presidential Election', event_time='November 3 2024'))

