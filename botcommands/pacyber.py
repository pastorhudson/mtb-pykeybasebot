import requests
from bs4 import BeautifulSoup
import os
import unicodedata
from datetime import datetime
from datetime import date
from datetime import timezone
from zoneinfo import ZoneInfo
from dateutil import tz

""" Copy and rename the secrets_env template in this repo to secrets.env.
    Add your own login and password for https://myschool.pacyber.org"""

""" Your login information below. It's probably best to store this in environment variables."""
tbLogin = os.environ.get('TBLOGIN')
tbPassword = os.environ.get('TBPASSWORD')

""" Uncomment below and comment out above if you're not using environment variables"""
# tbLogin = "login_id"
# tbPassword = "login_pass"

""" Internal URL that requires user to be logged in"""
SCRAPEURL = 'https://myschool.pacyber.org/FEGradebook.aspx'
# https://myschool.pacyber.org/FEGradebook.aspx

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

assignments_completed_today = 0
assignments_completed_this_week = 0

def get_last_activity(event_target, s):
    global assignments_completed_today
    global assignments_completed_this_week
    cur_assignments_completed = 0
    data = {
        "ctl00$sm": f"ctl00$ContentPlaceHolder1$GradebookInfo1$updatePanelGridViewCourses | ctl00$ContentPlaceHolder1$GradebookInfo1$gvCourses$ctl{event_target}$MyRadioButton1",
        "__EVENTTARGET": f"ctl00$ContentPlaceHolder1$GradebookInfo1$gvCourses$ctl{event_target}$MyRadioButton1",
        f"ctl00$ContentPlaceHolder1$GradebookInfo1$gvCourses$ctl{int(event_target) -1}$SelectGroup": "MyRadioButton1",
        f"ctl00$ContentPlaceHolder1$GradebookInfo1$gvCourses$ctl{event_target}$SelectGroup": "MyRadioButton1",
    }
    url = 'https://myschool.pacyber.org/FEGradebook.aspx'  # grade_url
    r = s.get(url, headers=headers)  # This is where we make the first request to generate an authenticity_token
    # print(r.content)
    soup = BeautifulSoup(r.content,
                         'html.parser')  # We're using Beautiful Soup to scrape the token form the page source
    # """Here we are populating data dictionary with the scraped auth tokens"""
    data['__VIEWSTATE'] = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
    data['__VIEWSTATEGENERATOR'] = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
    data['__EVENTVALIDATION'] = soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
    page = s.post(SCRAPEURL, data)
    bs = BeautifulSoup(page.content, 'html.parser')

    """ Grab the tables for the subjects and their corresponding info """
    try:
        activity_book_div = bs.find("div", {"id": "ctl00_ContentPlaceHolder1_GradebookInfo1_PanelCourseDetail"})
        activity_book_table = activity_book_div.find('table', {"id": "ctl00_ContentPlaceHolder1_GradebookInfo1_gvAssignment"})
        activity_book_rows = activity_book_table.findAll('tr')
        cur_date = ""
        last_date = ""
        for row in activity_book_rows:
            td = row.find_all('td')
            row = [unicodedata.normalize("NFKD", i.text) for i in td]
            """Get datetime for 'Aug 31, 2022'"""
            est = tz.gettz('America/New_York')
            today = datetime.today()
            today = today.astimezone(est)
            try:
                if last_date == "":
                    last_date = datetime.strptime(row[-1:][0], '%b %d, %Y')
                    cur_date = datetime.strptime(row[-1:][0], '%b %d, %Y')
                else:
                    cur_date = datetime.strptime(row[-1:][0], '%b %d, %Y')
                if last_date < cur_date:
                    last_date = cur_date
                if cur_date.date() == today.date():
                    assignments_completed_today += 1
                    cur_assignments_completed += 1
                if cur_date.isocalendar()[1] == date.today().isocalendar()[1]:
                    assignments_completed_this_week += 1
                # print(f"Current Date: {cur_date} - "
                #       f"Last Date: {last_date} - {row[-1:]}")
            except Exception as e:
                # print(e)
                pass
            # print(row[-1:])

    except Exception as e:
        return "Please Check your secrets.env and ensure your login and password are correctly set."
    # print(last_date)
    try:
        days = datetime.today() - last_date
        days = days.days
        last_date = f"{last_date.strftime('%b %m, %Y')} ({days} days)"
    except:
        days = 'NA'
    return last_date, cur_assignments_completed


def get_academic_snapshot():
    global assignments_completed_today
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
        login_data['__VIEWSTATE'] = bs.find('input', attrs={'name': '__VIEWSTATE'})['value']
        login_data['__VIEWSTATEGENERATOR'] = bs.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
        login_data['__EVENTVALIDATION'] = bs.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
        """ Grab the tables for the subjects and their corresponding info """
        try:
            grade_book_table = bs.find("table", {"id": "ctl00_ContentPlaceHolder1_GradebookInfo1_gvCourses"})
            grade_book_rows = grade_book_table.findAll('tr')

        except Exception as e:
            return "Please Check your secrets.env and ensure your login and password are correctly set."

        msg = ""
        for row in grade_book_rows:
            td = row.find_all('td')
            row = [unicodedata.normalize("NFKD", i.text) for i in td]
            last_activity = None
            for t in td:
                for tt in t.find_all('input'):
                    activity_table_id = tt.get('id').split("_")[4][3:]

                    last_activity = get_last_activity(activity_table_id, s)
            try:
                msg += "\n".join([f"```Subject: {row[2]}",
                                  f"Score: {row[5].split(' ')[0] or None}",
                                  f"Progress: {row[6]}",
                                  f"Last Date: {last_activity[0]}",
                                  f"Completed Today: {last_activity[1]}```",
                                  "\n"
                                  ])
                # msg += '```'
            except IndexError:
                print('Error')
                pass
        msg += f"Today: {assignments_completed_today}\n" \
               f"This Week: {assignments_completed_this_week}" \
               f"\n{datetime.now().astimezone()}"
        return msg


if __name__ == "__main__":
    # print(date.today())
    print(get_academic_snapshot())
    # print(datetime.now().astimezone())
    # day1 = 'Mar 21, 2023'
    # day2 = 'Apr 20, 2023'
    # first = datetime.strptime(day1, '%b %d, %Y')
    # second = datetime.strptime(day2, '%b %d, %Y')
    # now = datetime.now(timezone.utc)
    # est = tz.gettz('America/New_York')
    # print(now)
    # print(now.astimezone(est))
    # print(second.astimezone(timezone.utc))
    # print(second.isocalendar()[1])
    # print(first.isocalendar()[1])
    # Year, WeekNum, DOW = date.today().isocalendar()[1]