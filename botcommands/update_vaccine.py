from bs4 import BeautifulSoup
import requests
import urllib.parse
from urllib.parse import unquote
from pathlib import Path
import pandas as pd

SCRAPEURL = 'https://www.health.pa.gov/topics/disease/coronavirus/Pages/Vaccine.aspx'
storage = Path('./storage/')
BASEURL = "https://www.health.pa.gov"

"""Here is where we setup headers to make it look like a browser"""
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.99 Safari/537.36'
}


def download_vaccine_data():
    with requests.Session() as s:
        """Open a requests session, Store the correct auth headers."""
        url = 'https://www.health.pa.gov/topics/disease/coronavirus/Pages/Vaccine.aspx'
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        filedivs = soup.findAll("div", {"class": "ms-rtestate-field"})
        for div in filedivs:
            if "COVID-19 Vaccine Provider Locations" in div.text:
                a = div.find(href=True)
                file_url = urllib.parse.urljoin(BASEURL, a['href'])
                file_name = Path(f"./storage/{unquote(a['href'].split('/')[-1])}")
                r = requests.get(file_url, allow_redirects=True)
                open(file_name, 'wb').write(r.content)
                return


def get_vaccine_data():
    download_vaccine_data()
    excel_file = './storage/COVID-19 Vaccine_Provider Locations_Week 1.xlsx'
    vaccines = pd.read_excel(excel_file, engine='openpyxl')
    data_header = list(vaccines.columns)
    vaccine_dist = pd.DataFrame(vaccines, columns=data_header)
    clean = vaccine_dist.dropna()
    clean['Provider'] = clean['Provider Location'].str.slice(0, 18)

    msg = clean[['Provider', 'Doses']].to_markdown(index=False)
    return f"```\n{msg}\n```"


if __name__ == "__main__":
    download_vaccine_data()
    print(get_vaccine_data())
