from rcp import get_poll_data, get_polls
from prettytable import PrettyTable
from models import Team
from crud import s
import us


def get_poll_result(team_name):
    team = s.query(Team).filter_by(name=team_name).first()
    try:
        state = us.states.lookup(team.local[0].state)
    except Exception as e:
        pass
    poll_table = PrettyTable()
    poll_table.border = False
    poll_table.field_names = ["Poll", "Biden", "Trump", "Sp"]

    td = get_poll_data(
        "https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html"
    )
    # pa = get_poll_data("https://www.realclearpolitics.com/epolls/2020/president/pa/pennsylvania_trump_vs_biden-6861.html")
    # ky = get_poll_data("https://www.realclearpolitics.com/epolls/2020/president/ky/kentucky_trump_vs_biden-6915.html")
    # battle_grounds = "https://www.realclearpolitics.com/json/battleground_script/key_battleground_states_2020_spread_average_oct_23.json"
    # print(pa)
    message = "```\n"

    for row in td[0]["data"]:
        if row['Poll'] == 'RCP Average':
            message += f'National Real Clear Politics Average:\n' \
                       f'Date: {row["Date"]}\n' \
                       f'Biden: {row["Biden (D)"]}  ' \
                       f'Trump: {row["Trump (R)"]}\n' \
                       f'Spread: {row["Spread"]}\n\n'
    try:
        if state:
            spread_total = 0
            row_count = 0
            biden_total = 0
            trump_total = 0
            spread = 0
            message += f"{state}\n"
            for row in get_polls(state=str(state)):
                # print(row['result'].split(",")[0].strip().split(" ")[1])
                # print(row['result'].split(",")[1].strip().split(" ")[1])
                poll_name = (row["poll"][:13] + '..') if len(row['poll']) > 13 else row['poll']

                biden = int(row['result'].split(",")[0].strip().split(" ")[1])
                trump = int(row['result'].split(",")[1].strip().split(" ")[1])
                biden_total = biden + biden_total
                trump_total = trump + trump_total
                if biden > trump:
                    spread = biden - trump
                    biden = f"{biden}+"
                else:
                    spread = trump - biden
                    trump = f"{trump}+"
                poll_table.add_row([poll_name, biden, trump, spread])
                row_count += 1

            if biden_total > trump_total:
                spread_total = round(biden_total/row_count, 3) - round(trump_total/row_count, 3)
                biden_total = f"{round(biden_total/row_count, 1)}+"
                trump_total = round(trump_total/row_count, 1)
            else:
                spread_total = round(trump_total/row_count, 3) - round(biden_total/row_count, 3)
                biden_total = round(biden_total/row_count, 1)
                trump_total = f"{round(trump_total / row_count, 1)}+"

            poll_table.add_row(["Total", biden_total, trump_total, round(spread_total, 2)])

            poll_table.align = "l"
            # poll_table.sortby = '#'
            # poll_table.reversesort = True
            message += poll_table.get_string()
    except UnboundLocalError:
        message += "Set Team Local to get State Polling Data"


    # for row in pa[0]["data"]:
    #     if row['Poll'] == 'RCP Average':
    #         message += f'Pennsylvania Real Clear Politics Average:\n' \
    #                    f'Date: {row["Date"]}\n' \
    #                    f'Biden: {row["Biden (D)"]}  ' \
    #                    f'Trump: {row["Trump (R)"]}  ' \
    #                    f'Spread: {row["Spread"]}'

    message += "\n```"
    s.close()
    return message


if __name__ == '__main__':
    print(get_poll_result('morethanmarvin,pastorhudson'))
    # print(get_polls(state='Florida'))

