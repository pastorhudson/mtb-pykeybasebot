from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import random


# //meta[@property='og:title']
# //meta[@property='og:description']

observations = [":disappointed: :camera:",
                "Oh sure I'll load a random url to take a picture. What could possibly go wrong?",
                "I hope it comes back blank.",
                "It would literally be quicker to just click the link."]

def get_domain(url):
    print(urlparse(url).netloc)
    return urlparse(url).netloc


def get_youtube_id(url):
    yt_id = url.split('/')[3]
    if "watch?v=" in yt_id:
        print(yt_id[8:])
    return yt_id[8:]


def get_screenshot(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome('./chromedriver/chromedriver', options=chrome_options)

    driver.get(url)
    # domain = get_domain(url)
    try:
        element = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/'))
        )

    except Exception as e:
        print(e)
    finally:

        file = driver.save_screenshot("./screenshots/screenshot.png")

    driver.quit()
    payload = {"msg": random.choice(observations), "file": "./screenshots/screenshot.png"}
    print(payload)
    return payload


if __name__ == "__main__":

    get_screenshot('https://stackoverflow.com/questions/38077571/xpath-for-first-child-element-inside-body-tag')
