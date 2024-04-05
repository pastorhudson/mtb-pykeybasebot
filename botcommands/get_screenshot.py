from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import os
from PIL import Image



# //meta[@property='og:title']
# //meta[@property='og:description']

observations = [":disappointed: :camera:",
                "Oh sure I'll load a random url to take a picture. What could possibly go wrong?",
                "I hope it comes back blank.",
                "It would literally be quicker to just click the link.",
                "50,000 times more intelligent than a human, and yet I am used to take pictures."]


def get_youtube_id(url):
    yt_id = url.split('/')[3]
    if "watch?v=" in yt_id:
        print(yt_id[8:])
    return yt_id[8:]


def crop_screenshot(driver, filename):
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    driver.find_element_by_tag_name('body'). \
        screenshot(filename)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])
    print("Resizing & Cropping")
    with Image.open(filename) as im:
        # The crop method from the Image module takes four coordinates as input.
        # The right can also be represented as (left+width)
        # and lower can be represented as (upper+height).
        width, height = im.size

        resize_by = float(800 / width)
        resized_im = im.resize((800, int(float(height) * resize_by)))

        width, height = resized_im.size
        if height > 1700:
            (left, top, right, bottom) = (0, 0, width, height - (height - 1700))
            new_im = resized_im.crop((left, top, right, bottom))
            new_im.save(filename)
        else:
            resized_im.save(filename)


def get_screenshot(url):
    options = webdriver.ChromeOptions()
    # options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=options)
    driver = webdriver.Chrome(chrome_options=options)


    driver.get(url)
    # domain = get_domain(url)
    try:
        element = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/'))
        )

    except Exception as e:
        print(e)
    finally:

        # file = driver.save_screenshot(f"{os.environ.get('SCREENSHOT_DIR')}/screenshot.png")
        crop_screenshot(driver, os.path.join(os.environ.get('SCREENSHOT_DIR'), 'screenshot.png'))

    driver.quit()
    payload = {"msg": random.choice(observations), "file": f"{os.environ.get('SCREENSHOT_DIR')}/screenshot.png"}
    print(payload)
    return payload


if __name__ == "__main__":

    get_screenshot('https://twitter.com/joanpennnative/status/1450887248866594819?s=12')
