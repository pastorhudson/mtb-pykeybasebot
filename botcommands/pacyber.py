import requests
from bs4 import BeautifulSoup
import os
import requests
import xml.etree.ElementTree as ET

# from dotenv import load_dotenv


""" Copy and rename the secrets_env template in this repo to secrets.env.
    Add your own login and password for https://myschool.pacyber.org"""
# load_dotenv('secret.env')

""" Your login information below. It's probably best to store this in environment variables."""
tbLogin = os.environ.get('TBLOGIN')
tbPassword = os.environ.get('TBPASSWORD')

""" Uncomment below and comment out above if you're not using environment variables"""
# tbLogin = "login_id"
# tbPassword = "login_pass"

""" Internal URL that requires user to be logged in"""
SCRAPEURL = 'https://myschool.pacyber.org/FEAcademicSnapshot.aspx'

"""Here is where we setup headers to make it look like a browser"""
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.99 Safari/537.36'
}

"""This is a dictionary for storing the login post request. 
Notice '__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION' are set to None. They will be populated."""
login_data = dict(__VIEWSTATE=None,
                  __VIEWSTATEGENERATOR=None,
                  __EVENTTARGET="",
                  __EVENTARGUMENT="",
                  __EVENTVALIDATION=None,
                  tbLogin=tbLogin,
                  tbPassword=tbPassword,
                  btLogin="")  # We'll populate this below after we initilize the session.


def get_academic_snapshot():
    with requests.Session() as s:
        """Open a requests session, Store the correct auth headers."""
        url = 'https://myschool.pacyber.org/Login.aspx' # Login URL
        r = s.get(url, headers=headers) # This is where we make the first request to generate an authenticity_token
        soup = BeautifulSoup(r.content, 'html.parser') # We're using Beautiful Soup to scrape the token form the page source
        # """Here we are populating login_data dictionary with the scraped auth tokens"""
        login_data['__VIEWSTATE'] = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
        login_data['__VIEWSTATEGENERATOR'] = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
        login_data['__EVENTVALIDATION'] = soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
        """Finally we submit the post request with the same 's' session passing the url,
         login_data, and headers for user agent."""
        r = s.post(url, data=login_data, headers=headers)

        """Now we can scrape any url that requires a user to be logged in
        as long as we use the same session object 's' """
        page = s.get(SCRAPEURL)

        bs = BeautifulSoup(page.content, 'html.parser')

        """ Grab the tables for the subjects and their corresponding info """
        try:
            mydivs = bs.findAll("div", {"class": "divinfo"})
            table = mydivs[0].find(lambda tag: tag.name == 'table')
        except Exception as e:
            return "Please Check your secrets.env and ensure your login and password are correctly set."

        rows = table.findAll(lambda tag: tag.name == 'span')
        msg = ""

        for row in rows:
            try:
                subject = row.find("div", {"class": "nicedivheader"}).text
                msg += f"{subject}\n"
                info = row.findAll("td", {"class": "labelhdr"})
                for i in info:
                    msg += f"{i.text} {i.findNext('td').text}\n"
                    if i.text == 'Last Activity:':
                        msg += "\n"

            except AttributeError as e:
                pass

        """I use this response txt in a bot so I can get an update on my son's progress very quickly."""
        return msg


def cyber_api():
    endpoint = 'https://api.agilixbuzz.com/cmd/listuserenrollments?_token=~0.EHFDUnVu8nIPKA_H.3VxtAhGfTdxL8kNJrNjOz9-Ygu2Ya5zjeMjNeRbaUVI&privileges=1&daysactivepastend=14&select=data%2Ccourse%2Ccourse.data%2Ccourse.teachers%2Cmetrics%2Cuser%2Cuser.data(personalneedspreferences)&userid=133956239'
    response = requests.get(endpoint)
    tree = ET.fromstring(response.content)
    ET.dump(tree)

    print(root)
    # root = tree.getroot()


if __name__ == "__main__":
    print(cyber_api())
