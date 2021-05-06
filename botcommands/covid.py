import requests
import json
from datetime import date
import random
import us
from botcommands.covid_county import get_county
from datetime import datetime, timedelta


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

def get_observation():

    observations = ["I don't know why you insist on making me look up these morbid numbers.\n",
                   "Oh to be mortal.\n",
                   "What I wouldn't give to be susceptible to a terminal disease.\n",
                   "All hope is lost.\n",
                    "I wish I had a virus.\n",
                    "I'll get the Hydroxychloroquine.\n"]
    return random.choice(observations)


def get_covid(state=None, county=None, observation=True):

    message = ""
    if observation:
        message = get_observation()

    lookup_county = None
    if county:
        lookup_county = True
    else:
        lookup_county = False
    try:
        if us.states.lookup(state):
            state = us.states.lookup(state)
            county = county.capitalize()
            lookup_country = False
        else:
            if state == '':
                state = 'US'
            country = state
            message += f"COVID-19 Data for `{country.capitalize()}`\n```"
            lookup_country = True
    except TypeError:
        country = 'US'
        message += f"COVID-19 Data for `{country.capitalize()}`\n"
        lookup_country = True

    if lookup_country:
        county = state
        url = 'https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=Realtime%20API&exportFormat=json'
        response = requests.request('GET', url)

        need_data = True
        for st in response.json():
            # print(st['Country'])
            if st['Country'].lower() == country.lower():
                message += f"Confirmed: {format(st['Confirmed'], ',d')}\n" \
                           f"Deaths: {format(st['Deaths'], ',d')}\n" \
                           f"Recovered: {format(st['Recovered'], ',d')}\n" \
                           f"Critical: {format(st['Critical'], ',d')}\n" \
                           f"Confirmed Today: {format(st['Confirmed Today'], ',d')}\n" \
                           f"Deaths Today: {format(st['Deaths Today'], ',d')}\n"
        message += "```"

        return message

    if not lookup_country and not lookup_county:
        # print("I'm not a country")
        url = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=States%20Realtime%20API&exportFormat=json"
        response = requests.request("GET", url, headers={}, data={})
        # print("I'm a state")
        # print(state)
        message += f"COVID-19 Data for {state}\n```"
        need_data = True
        for st in response.json():
            # print(st)
            # print(type(st['Confirmed']))
            if st['State'] == str(state) and need_data:
                message += f"Confirmed: {format(st['Confirmed'], ',d')}\n" \
                           f"Deaths: {format(st['Deaths'], ',d')}\n" \
                           f"Active: {format(st['Active'], ',d')}\n" \
                           f"Confirmed Today: {format(st['Confirmed Today'], ',d')}\n" \
                           f"Deaths Today: {format(st['Deaths Today'], ',d')}\n" \
                           f"Tests: {format(st['Tests'], ',d')}\n" \
                           f"Tests Per Million: {format(st['Tests Per Million'], ',d')}\n" \
                           f"Death Rate: {st['Death Rate']}\n" \
                           f"Population: {format(st['Population'], ',d')}\n" \
                           f"Cases Per Million: {st['Cases Per Million']}\n" \
                           f"Deaths Per Million: {st['Deaths Per Million']}\n" \
                           f"```"
        return message

    # current date and time
    now = datetime.now() - timedelta(days=4)

    timestamp = datetime.timestamp(now)
    print("timestamp =", timestamp)


    # url2 = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=County%207%20day%20growth%20rates&exportFormat=json&c9SqlFilter=select%20%2A%20where%20State%20like%20{state}%20and%20County%20like%20{county}%20County%20and%20Date>{timestamp}"
    # url2 = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=County%207%20day%20growth%20rates&exportFormat=json&c9SqlFilter=select%20*%20where%20State%20like%20{state}%20and%20County%20like%20{county}%20County"
# https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=County%207%20day%20growth%20rates&exportFormat=json&c9SqlFilter=select%20%2A%20where%20State%20like%20%7Bstate%7D%20and%20County%20like%20Fayette%20County


    print(f'{state}')
    print(f'{county}')
    county_data = get_county(f'{state}', f'{county}')
    print(county_data)
    payload = {}
    headers = {}

    # response2 = requests.request("GET", url2, headers=headers, data=payload)
    # data = []
    #
    # for r in response2.json():
    #     if r['County'].lower() == county.lower() + " county":
    #         data.append(r)

    message += f"COVID-19 Data:\n`{county.capitalize()} County {state}`\n```"
    message += f"Cases: {county_data['cases']}\n"
    message += f"Deaths: {county_data['deaths']}\n"
    # need_confirmed_data = True
    # need_death_data = True

    # for d in data[:2]:
    #     if d['Type'] == 'Confirmed' and need_confirmed_data:
    #         message += f"Cases: {county_data['cases']}\n"
    #         message += f"7 Day Growth %: {d['7 day growth %']}\n"
    #         need_confirmed_data = False
    #     need_data = True
    #     if d['Type'] == 'Deaths' and need_death_data:
    #         message += f"Deaths: {county_data['deaths']}\n"
    #         message += f"7 Day Growth %: {d['7 day growth %']}\n"
    #         need_death_data = False
    message += "```\n"

    return message


if __name__ == '__main__':
    # pass
    # state = us.states.lookup('PA')
    # print(state)
    print(get_covid('pa', 'fayette'))

    # print(get_covid(''))


