from crud import s
from models import Team, User


def get_team_user(team_name, username):
    team = s.query(Team).filter_by(name=team_name).first()
    user = s.query(User).filter_by(username=username).first()

    return team, user


def get_team(team_name):
    team = s.query(Team).filter_by(name=team_name).first()

    return team
