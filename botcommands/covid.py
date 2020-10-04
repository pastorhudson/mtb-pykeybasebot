import requests
import json
from datetime import date
import random

#
# States Testing Data Current	covidtracking.com
# States Testing Historical	covidtracking.com
# Raw County level Data	https://static.usafacts.org/
# Latest Day County Level Data	https://static.usafacts.org/
# County 7 day growth rates	https://static.usafacts.org/
# States Realtime API	corona.lmao.ninja
# Realtime API	corona.lmao.ninja
# John Hopkins Coronavirus Dataset	John Hopkins
# John Hopkins Coronavirus Dataset US Only	John Hopkins
# Death Projections and Hospital Projections	covid19.healthdata.org — IHME
# MIT Model Hospitalization and Deaths Projections	https://www.covidanalytics.io/projections — MIT Model
# Columbia University Model Hospitalization and Deaths Projections

observations = "I don't know why you insist on making me look up the morbid numbers." \
               "Oh to be mortal." \
               "What I wouldn't give to be susceptible to a terminal disease." \
               "All hope is lost."


def get_covid(state, county):
    # today = date.today()
    # dd/mm/YY
    # today = today.strftime("%m/%d/%Y")
    url = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=Latest%20Day%20County%20Level%20Data&exportFormat=json&c9SqlFilter=select%20*%20where%20State%20like%20{state}"
    url2 = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=County%207%20day%20growth%20rates&exportFormat=json&c9SqlFilter=select%20*%20where%20State%20like%20{state}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    response2 = requests.request("GET", url2, headers=headers, data=payload)

    data = []
    # for r in response.json():
    #     # print(r['County'])
    #     if r['County'] == county + " County":
    #         data.append(r)

    # data2 = []
    for r in response2.json():
        # print(r['County'])
        if r['County'] == county + " County":
            # print(r)
            data.append(r)
    # print(data)

    message = f"{random.choice(observations)}" \
              f"```\n" \
              f"COVID-19 Data for {county} County {state}\n" \

    need_data = True
    for d in data[:2]:
        print(d)
        if d['Type'] == 'Confirmed' and need_data:
            message += f"Confirmed Cases: {d['values']}\n"
            message += f"7 Day Growth %: {d['7 day growth %']}\n"
            need_data = False
        need_data = True
        if d['Type'] == 'Deaths' and need_data:
            message += f"Deaths: {d['values']}\n"
            message += f"7 Day Growth %: {d['7 day growth %']}\n"
            need_data = False
    message += "```"

    return message


if __name__ == '__main__':
    pass
    # get_covid('Tennessee', 'Dyer')
    # get_covid('Pennsylvania', 'Fayette')

