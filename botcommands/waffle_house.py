import requests
from prettytable import PrettyTable


def get_waffle_closings(state: str = None):
    x = PrettyTable()
    x.field_names = ["Store", "State", "City"]
    msg = f"```Waffle House Index\nCurrently Closed Waffle House Locations:\n"
    for store in get_waffles(state)['stores']:
        x.add_row([store['name'], store['state'], store['city']])
    x.align = "r"
    x.padding_width = 2
    x.sortby = "State"
    x.reversesort = True
    print(x)
    msg += f"{x}```"

    return msg


def get_waffles(state: str = None):
    if state:
        closings = requests.get(f'https://wafflehouseindex.live/stores/closed?state={state}')
    else:
        closings = requests.get(f'https://wafflehouseindex.live/stores/closed')

    return closings.json()


if __name__ == '__main__':
    print(get_waffle_closings())
