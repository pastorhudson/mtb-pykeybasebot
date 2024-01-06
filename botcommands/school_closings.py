import random
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable


def get_closings():
    # Make a request to the website
    response = requests.get("https://assets1.cbsnewsstatic.com/Integrations/SchoolClosings/PRODUCTION/CBS/kdka/NEWSROOM/KDKAclosings.xml")
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'xml')

    # Find all 'closing' tags in the XML
    closings = soup.find_all('RECORD')

    return closings


def get_closings_list():
    closings = get_closings()

    # Define columns for Pretty Table
    table = PrettyTable(['Name', 'Status'])

    # For each closing, check if it's one of the specified organizations
    for closing in closings:
        name = closing.find('FORCED_ORGANIZATION_NAME').text
        status = closing.find('COMPLETE_STATUS').text
        table.add_row([name, status])
    return table


def search_closings(specific_words=None):
    closings = get_closings()

    # Define columns for Pretty Table
    table = PrettyTable(['Name', 'Status'])
    no_school = True
    # For each closing, check if it's one of the specified organizations
    for closing in closings:
        name = closing.find('FORCED_ORGANIZATION_NAME').text
        if any(word in name.lower() for word in specific_words):
            no_school = False
            status = closing.find('COMPLETE_STATUS').text
            table.add_row([name, status])

    if no_school:
        table.add_row(["Your Mom", "Open For Business"])

    return table


def get_school_closings(search=None, observation=True):
    if search:
        table = search_closings(search)
    else:
        table = get_closings_list()

    observation = [
        "I hope you have school",
        "Isn't learning wonderful",
        "No Sleep for you."
    ]

    if observation:
        payload = {'msg': f"{random.choice(observation)}\n"
                          f"```{table}"
                          f"```",}
    else:
        payload = {'msg': f"```{table}"
                          f"```",}
    return payload


if __name__ == "__main__":
    schools = "!school uniontown, Albert"
    schools = schools[7:].lower().strip().split(",")
    schools = [school.strip() for school in schools]
    print(schools)
    # specific_words = ["Albert Gallatin", "uniontown", "North Hills"]
    print(get_school_closings(schools))

# schools = "!school Uniontown, Albert Gallatin"
# schools = schools[7:].strip().split(",")
# print(schools)
# specific_words = ["Albert Gallatin", "Uniontown", "North Hills"]
# print(get_school_closings([school.strip() for school in schools]))