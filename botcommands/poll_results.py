from rcp import get_poll_data
from prettytable import PrettyTable


def get_polls():
    x = PrettyTable()

    td = get_poll_data(
        "https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html"
    )
    pa = get_poll_data("https://www.realclearpolitics.com/epolls/2020/president/pa/pennsylvania_trump_vs_biden-6861.html")
    # ky = get_poll_data("https://www.realclearpolitics.com/epolls/2020/president/ky/kentucky_trump_vs_biden-6915.html")


    # x.field_names = list(td[0]["data"][0].keys())
    # x.align = "l"
    # x.add_row(['NATIONAL',"" ,"" ,"" ,"" ,"" ,""])

    message = "```\n"

    for row in td[0]["data"]:
        if row['Poll'] == 'RCP Average':
            message += f'National Real Clear Politics Average:\n' \
                       f'Date: {row["Date"]}\n' \
                       f'Biden: {row["Biden (D)"]}  ' \
                       f'Trump: {row["Trump (R)"]}  ' \
                       f'Spread: {row["Spread"]}\n\n'

    x.add_row(['PENNSYLVANIA', '', '', '', '', '', ''])
    for row in pa[0]["data"]:
        if row['Poll'] == 'RCP Average':
            message += f'Pennsylvania Real Clear Politics Average:\n' \
                       f'Date: {row["Date"]}\n' \
                       f'Biden: {row["Biden (D)"]}  ' \
                       f'Trump: {row["Trump (R)"]}  ' \
                       f'Spread: {row["Spread"]}'


    message += "\n```"
    return message


if __name__ == '__main__':
    print(get_polls())