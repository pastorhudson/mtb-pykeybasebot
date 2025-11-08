from playwright.sync_api import sync_playwright
import random
import os
from PIL import Image

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


def crop_screenshot(page, filename):
    # Get the full page dimensions
    required_width = page.evaluate('() => document.body.parentNode.scrollWidth')
    required_height = page.evaluate('() => document.body.parentNode.scrollHeight')

    # Set viewport size to capture full content
    page.set_viewport_size({"width": required_width, "height": required_height})

    # Take screenshot of the body element to avoid scrollbar
    page.locator('body').screenshot(path=filename)

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to URL and wait for network to be idle (page fully loaded)
            page.goto(url, wait_until='load', timeout=30000)

            # Optional: Add a small additional wait for any animations/lazy loading
            page.wait_for_timeout(1000)

            # Take and process the screenshot
            crop_screenshot(page, os.path.join(os.environ.get('SCREENSHOT_DIR'), 'screenshot.png'))

        except Exception as e:
            print(e)
        finally:
            browser.close()

    payload = {"msg": random.choice(observations), "file": f"{os.environ.get('SCREENSHOT_DIR')}/screenshot.png"}
    print(payload)
    return payload


if __name__ == "__main__":
    get_screenshot('https://twitter.com/joanpennnative/status/1450887248866594819?s=12')