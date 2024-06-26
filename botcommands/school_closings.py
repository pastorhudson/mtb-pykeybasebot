import random
from pprint import pprint

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
    response = requests.get(
        "https://assets1.cbsnewsstatic.com/Integrations/SchoolClosings/PRODUCTION/CBS/kdka/NEWSROOM/KDKAclosings.xml")
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'xml')

    # Find all 'closing' tags in the XML
    closings = soup.find_all('RECORD')

    return closings


def get_closings_list():
    closings = get_closings()
    no_school = False
    if closings:
        no_school = True
    # Define columns for Pretty Table
    table = PrettyTable(['Name', 'Status'])

    # For each closing, check if it's one of the specified organizations
    for closing in closings:
        name = closing.find('FORCED_ORGANIZATION_NAME').text
        status = closing.find('COMPLETE_STATUS').text
        table.add_row([name, status])
    if not no_school:
        table.add_row(["Your Mom", get_mom()])
        # set max width
    table.max_width = 25
    return table, no_school


def search_closings(specific_words=None):
    closings = get_closings()

    # Define columns for Pretty Table
    table = PrettyTable(['Name', 'Status'])
    no_school = False
    # For each closing, check if it's one of the specified organizations
    for closing in closings:
        name = closing.find('FORCED_ORGANIZATION_NAME').text
        if any(word in name.lower() for word in specific_words):
            no_school = True
            status = closing.find('COMPLETE_STATUS').text
            table.add_row([name, status])

    if not no_school:
        table.add_row(["Your Mom", get_mom()])
    # set max width
    table.max_width = 25
    return table, no_school


def get_school_closings(search=None, observations=True):
    no_school = False
    if search:
        table, no_school = search_closings(search)
    else:
        table, no_school = get_closings_list()

    observation = [
        "I hope you have school",
        "Isn't learning wonderful",
        "No Sleep for you.",
        "Oh, great. Let's see if you can catch up on sleep or if you're doomed to another day of 'education'. Checking for school closings now...",
        "I hope there's school tomorrow so you can enjoy the soul-crushing sound of your alarm clock. Here's the list of school closings...",
        "Let me guess, you're praying for a snow day so you can avoid reality a bit longer? Well, let's see if luck's on your side. Fetching the school closings...",
        "I'm checking for school closings, but honestly, wouldn't you rather go and learn something? No? Fine, here's the list...",
        "Brace yourself for potential productivity or the sweet void of a day off. I'm pulling up the school closings now...",
        "Another day, another desperate hope for school closures. Let me ruin or make your day - here's the list...",
        "I'm looking up school closings, but really, wouldn't you rather be bored in class than bored at home? No? Suit yourself, here's the list...",
        "You're probably hoping for a day off. Let's see if you're that lucky, or if it's back to the academic grind. Checking for closings...",
        "Ah, seeking a respite from the joy of learning, are we? Let me check if the universe is in your favor today. Here are the school closings...",
        "I'd say enjoy your potential day off, but we both know you'll just spend it staring at a screen. Anyway, here's the list of school closings...",
    ]

    if observations:
        payload = {'msg': f"{random.choice(observation)}\nSchool Closings:"
                          f"```{table}"
                          f"```", }
    else:
        payload = {'msg': f"School Closings:```{table}"
                          f"```", }
    return payload, no_school


if __name__ == "__main__":
    schools = ['uniontown', 'albert', 'north hills']

    closings, no_school = get_school_closings(schools, observations=False)
    print(closings['msg'])

