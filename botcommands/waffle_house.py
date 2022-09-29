import requests
from prettytable import PrettyTable


def get_waffle_closings(state: str = None):
    x = PrettyTable()
    x.field_names = ["Store", "State", "City"]
    msg = f"```Waffle House Index\nCurrently Closed Waffle House Locations:\n"
    for store in get_waffles(state)['stores']:
        if len(store['city']) > 12:
            city = store['city'][0:10].strip() + ".."
        else:
            city = store['city']
        x.add_row([f"#{store['name'].split('#')[1]}", store['state'], city])
    x.align = "l"
    x.padding_width = 1
    x.sortby = "State"
    x.reversesort = True
    # print(x)
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
    # print('!waffle fl'[7:].strip())
    # print(f'Waffle House #703'.split('#')[1])
