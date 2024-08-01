import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden'

# create 'headers' and use them in your 'requests'
# create a header so the website thinks this is a web-browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like
# save your response
r = requests.get(url, headers=headers)

print(r.status_code)
print(r.url)

#save soup
soup = BeautifulSoup(r.text, 'html.parser')

#grab all tables
tables = soup.find_all('table', class_="w-full")
#only use the second table 'table[1]'
table = tables[0]

# create a list of rows and turn this list into a df
tlist = []
for tr in table.find_all('tr'):
    td = tr.find_all('td')

    # get the info from the header for labels
    if len(tr.find_all('th')) != 0:
        row = [i.text for i in tr.find_all('th')]
    else:
        row = [i.text for i in td]  # turn each row'sinfo into a list of info
    tlist.append(row)

# create df using first entry in tlist as column header
df = pd.DataFrame(tlist[1:], columns=tlist[0])
df.head(3)
print(df.all())
