import datetime


def get_keep():
    observations = [
        'The end is coming.'
    ]

    election = datetime.date(2020, 11, 3)

    days = election - datetime.date.today()

    msg = f"\nThere are {days.days} days till the US Presidental Election."

    return msg


if __name__ == "__main__":
    print(get_keep())
