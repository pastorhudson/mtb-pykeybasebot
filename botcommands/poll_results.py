import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

# URL to scrape
url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden'  # Replace with the actual URL

# Send a GET request to the URL
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table with class 'w-full'
table = soup.find('table', class_='w-full')

# Initialize a PrettyTable object
pretty_table = PrettyTable()

# Check if the table is found
if table:
    # Get all the rows in the table
    rows = table.find_all('tr')

    # Extract and add the header row to the PrettyTable
    header = rows[0].find_all('th')
    header = [th.text.strip() for th in header]
    pretty_table.field_names = header

    # Extract and add all the data rows to the PrettyTable
    for row in rows[1:]:
        columns = row.find_all('td')
        columns = [col.text.strip() for col in columns]
        pretty_table.add_row(columns)

    # Print the table
    print(pretty_table)
else:
    print("Table with class 'w-full' not found.")
