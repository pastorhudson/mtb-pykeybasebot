import random
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable


def get_mom():
    moms = [
        "is so caring, she could make a grizzly bear say 'please' and 'thank you'.",
        "is so creative, Picasso's paintings look like stick figures next to her crafts.",
        "is so wise, Yoda texts her for advice.",
        "is so good at gardening, her plants water themselves out of respect.",
        "is so organized, her to-do lists have their own to-do lists.",
        "is so skilled in the kitchen, her soup has won Nobel Prizes.",
        "is so positive, she makes optimists look like pessimists.",
        "is so graceful, ballerinas watch her to learn new moves.",
        "is so energetic, she makes the Energizer Bunny look lazy.",
        "is so punctual, even Father Time checks his watch with her.",
        "is so knowledgeable, Google uses her for searches.",
        "is so strong, superheroes ask her for workout tips.",
        "is so patient, she could teach a stone to wait.",
        "is so kind-hearted, Mother Teresa took notes.",
        "is so fashionable, the red carpet rolls itself out for her.",
        "is so talented, she could juggle with her eyes closed and one hand tied behind her back.",
        "is so charming, she could sell ice to a snowman.",
        "is so humorous, stand-up comedians take notes at her dinner table.",
        "is so generous, billionaires ask her for tips on giving.",
        "is so incredible, legends tell stories about her.",
        "is so nurturing, plants grow towards her voice.",
        "is so brilliant, her ideas light up the room.",
        "is so efficient, she finished her to-do list for tomorrow, today.",
        "is so dedicated, she could teach perseverance a lesson.",
        "is so lovely, flowers blush in her presence.",
        "is so respectful, manners use her as a role model.",
        "is so wonderful, she makes every day feel like a holiday.",
        "is so radiant, the sun gets jealous.",
        "is so delightful, her laughter cures sadness.",
        "is so phenomenal, history books are planning to include her.",
        "is so outstanding, she gets a standing ovation just for walking into a room.",
        "is so engaging, even introverts want to chat with her.",
        "is so awe-inspiring, she makes mountains look like hills.",
        "is so amazing, she could make onions cry out of joy.",
        "is so incredible, superheroes model themselves after her.",
        "is so admirable, even mirrors stop to look at her.",
        "is so extraordinary, the dictionary uses her picture as the definition.",
        "is so spectacular, fireworks watch her on the 4th of July.",
        "is so sweet, sugar takes notes.",
        "is so warm-hearted, she could make the North Pole melt.",
        "is so magnetic, compasses point towards her.",
        "is so lovable, even cats want to cuddle her.",
        "is so compelling, she could persuade water to flow uphill.",
        "is so stunning, even peacocks are envious.",
        "is so extraordinary, aliens visit Earth just to meet her.",
        "is so nurturing, Mother Nature asks her for tips.",
        "is so fantastic, fairy tales are jealous.",
        "is so awesome, she could make Mondays feel like Fridays.",
        "is so remarkable, history books reserve a chapter for her.",
        "is so inspiring, motivational speakers go to her for pep talks.",
    ]
    return random.choice(moms)

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
        table.add_row(["Your Mom", get_mom()])

    return table, no_school


def get_school_closings(search=None, observations=True):
    no_school = False
    if search:
        table, no_school = search_closings(search)
    else:
        table = get_closings_list()

    observation = [
        "I hope you have school",
        "Isn't learning wonderful",
        "No Sleep for you."
    ]

    if observations:
        payload = {'msg': f"{random.choice(observation)}\nSchool Closings:"
                          f"```{table}"
                          f"```",}
    else:
        payload = {'msg': f"School Closings:```{table}"
                          f"```",}
    return payload, no_school


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