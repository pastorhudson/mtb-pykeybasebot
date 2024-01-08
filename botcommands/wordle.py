import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dateutil import parser
import random
import logging

logging.basicConfig(level=logging.DEBUG)

def scrape_wordle(date_to_query=None):

    if date_to_query:
        date_to_query = parser.parse(date_to_query).strftime("%Y/%m/%d")
        url = f"https://www.nytimes.com/{date_to_query}/crosswords/wordle-review.html"
    else:
        today = datetime.today().strftime("%Y/%m/%d")
        url = f"https://www.nytimes.com/{today}/crosswords/wordle-review.html"
    # Setting up Chrome options for headless browsing and custom User-Agent
    options = Options()
    options.headless = True
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=options)
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

    # Path to your WebDriver (e.g., chromedriver)

    driver_path = os.environ.get('CHROMEDRIVER_PATH')

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(options=options, executable_path=driver_path)

    # Open the URL
    driver.get(url)

    # Wait for JavaScript to load (if necessary)
    driver.implicitly_wait(5)  # Adjust the time according to your needs

    # Find the element containing "Today's word"
    # You might need to adjust the selector according to the webpage structure
    try:
        element = driver.find_element(By.CSS_SELECTOR,
                                      "div.css-s99gbd:nth-child(8) > div:nth-child(1) > p:nth-child(2)")
        msg = element.text
        logging.info(element.text)
    except Exception as e:
        msg = None
        print("Error:", e)

    # Close the browser
    logging.info(driver.page_source)
    driver.quit()

    return msg


def get_wordle(date_to_query=None):
    observation = [
        "You dirty cheater",
        "May you prevail over your enemies with your ill gotten gain",
        "It's so depressing to see you like this",
        "RIGGED!!!"
    ]

    text = scrape_wordle(date_to_query)
    if text is None:
        msg = """The word is escaping me."""
    msg = (f"{random.choice(observation)}"
           f"```"
           f"{text}"
           f"```")

    return msg


async def async_get_wordle(date_to_query=None):
    # Optionally, create a ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=2)

    # Run the get_wordle function in the executor
    result = await asyncio.run_in_executor(executor, get_wordle, date_to_query)

    # Close the executor
    executor.shutdown()

    return result

if __name__ == "__main__":
    result = asyncio.run(async_get_wordle(date_to_query="jan 5 2024"))
    print(result)
