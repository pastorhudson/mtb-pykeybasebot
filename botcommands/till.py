import datetime
# import random


def get_observation():
    observations = [
        'The end is coming.',
        'Counting the days.'
    ]
    return observations[0]


def get_till(observation=True):
    msg = ""
    if observation:
        msg = get_observation()

    till = datetime.date(2020, 12, 25)

    days = till - datetime.date.today()

    msg = f"\nThere are `{days.days}` days till Christmas!\n"

    return msg


if __name__ == "__main__":
    print(get_till())
