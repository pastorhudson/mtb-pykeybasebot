import gspread
import pandas as pd
from datetime import datetime
import os
import json

# print(os.environ.get('google_p_key'))

credentials = json.loads(os.environ.get('google_p_key'))

gc = gspread.service_account_from_dict(credentials)

sh = gc.open_by_key("1b9o6uDO18sLxBqPwl_Gh9bnhW-ev_dABH83M5Vb5L8o")

worksheet = sh.sheet1
dataframe = pd.DataFrame(worksheet.get_all_records())
last_date = sh.sheet1.get('C2')[0][0]
last_date = datetime.strptime(last_date, "%m/%d/%y")
tspan = datetime.now() - last_date
days_this_year = (datetime.now() - datetime(datetime.now().year, 1, 1)).days
# print(days_this_year)


def get_years_avarage():
    start_year = 1982
    year_avg = []
    while start_year < datetime.now().year:
        df = dataframe[dataframe['year'] == start_year]
        avg = int(df.count()[['case']].to_string(index=False)) / 365
        year_avg.append(avg)
        start_year += 1
    chance = 100 - (sum(year_avg) / len(year_avg) * 100)
    # print(year_avg)
    return round(chance, 2)


def get_weapon():
    n = 5
    weapons = dataframe['weapon_type'].value_counts()[:n].index.tolist()
    w_msg = "Top 5 Frequently used Weapons:\n"
    for weapon in weapons:
        w_msg += f"- {weapon}\n"
    return w_msg


def get_morbid():
    # selecting rows based on condition
    rslt_df = dataframe[dataframe['year'] == datetime.now().year]

    # print(rslt_df[["case", "fatalities", "injured", "mental_health_details"]])
    msg = f"Mass Shooting Data for {datetime.now().year}\n"
    msg += f"```Cases: {rslt_df.count()[['case']].to_string(index=False)}\n"
    msg += rslt_df.sum()[['injured', 'fatalities']].to_string()
    # msg +=
    msg += f"\nDays since last case: {tspan.days}\n" \
           f"{get_years_avarage()}% likelyhood there is no mass shooting today```"

    msg += "A mass shooting is 3 or more people being killed.\n" \
           "We are tracking random acts unrelated to other disputes or rivalries.\n"

    msg += "Other Data:\n```"
    msg += f"{get_weapon()}```"

    return msg
#
#
# if __name__ == "__main__":
#     print(get_morbid())