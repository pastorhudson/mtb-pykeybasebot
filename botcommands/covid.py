import requests
import json
from datetime import date

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
    for r in response.json():
        # print(r['County'])
        if r['County'] == county + " County":
            data.append(r)

    data2 = []
    for r in response2.json():
        # print(r['County'])
        if r['County'] == county + " County":
            data2.append(r)

    message = f"I don't know why you insist on seeing this.\n" \
              f"```\n" \
              f"Confirmed Cases for {county} County {state}\n" \
              f"7 day Growth %: {data2[0]['7 day growth %']}\n" \
              f"Total Count: {data[1]['values']}\n" \
              f"Deaths for {county} County {state}\n" \
              f"Growth %: {data2[1]['7 day growth %']}\n" \
              f"Total Count: {data[0]['values']}\n" \
              f"```"
    return message


if __name__ == '__main__':
    get_covid('Pennsylvania', 'Fayette')
