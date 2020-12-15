import csv
import requests
import json


def get_county(state, county):

    with open('./storage/covid-19-data/live/us-counties.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # print(row)

            if row['county'] == county and row['state'] == state:
                return row


def get_county_7_day(state, county):
    message = ""
    url2 = f"https://knowi.com/api/data/ipE4xJhLBkn8H8jisFisAdHKvepFR5I4bGzRySZ2aaXlJgie?entityName=County%207%20day%20growth%20rates&exportFormat=json&c9SqlFilter=select%20*%20where%20State%20like%20{state}"
    county_data = get_county(f'{state}', f'{county}')

    payload = {}
    headers = {}

    response2 = requests.request("GET", url2, headers=headers, data=payload)
    data = []

    for r in response2.json():
        if r['County'].lower() == county.lower() + " county":
            data.append(r)

    message += f"COVID-19 Data:\n`{county.capitalize()} County {state}`\n```"
    need_confirmed_data = True
    need_death_data = True



    for d in data[:2]:
        if d['Type'] == 'Confirmed' and need_confirmed_data:
            message += f"Cases: {county_data['cases']}\n"
            message += f"7 Day Growth %: {d['7 day growth %']}\n"
            need_confirmed_data = False
        need_data = True
        if d['Type'] == 'Deaths' and need_death_data:
            message += f"Deaths: {county_data['deaths']}\n"
            message += f"7 Day Growth %: {d['7 day growth %']}\n"
            need_death_data = False
    message += "```\n"

    return message


def get_county_7_csv(state, county):

    with open('./storage/7day.csv', mode='r') as csv_file:
        for row in csv_file:
            try:
                print(row)
                data = json.loads(row.strip()[:-1])
                # print(data['County'])
                # if data['County'] == 'Fayette' + ' County':
                #     print(data["7 day growth %"])
            except Exception as e:
                print(e)

            # if row['County'] == county and row['State'] == state:
            #     return row


def get_county_vaccine(state, county):
    pd.read_excel('/storage/COVID-19 Vaccine_Provider Locations_Week 1.xlsx', index_col=0)


if __name__ == "__main__":
    # print(get_county('Pennsylvania', "Fayette"))
    print(get_county_vaccine('Pennsylvania', 'Fayette'))
    # print(get_county_7_csv('Pennsylvania', 'Fayette'))
