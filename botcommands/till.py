import datetime
# import random


def get_observation():
    observations = [
        'The end is coming.'
    ]
    return observations[0]


def get_till(observation=True):
    msg = ""
    if observation:
        msg = get_observation()

    election = datetime.date(2020, 11, 3)

    days = election - datetime.date.today()

    msg = f"\nThere are `{days.days}` days till the US Presidental Election."

    return msg


if __name__ == "__main__":
    print(get_till())
