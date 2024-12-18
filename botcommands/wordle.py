import ast
import random
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def solve_wordle(debug=True, headless=True):
    """
    Attempts to solve the daily Wordle puzzle using Selenium.

    Args:
        debug (bool): If True, prints debug information during solving
        headless (bool): If True, runs Chrome in headless mode

    Returns:
        tuple: (str, int) containing the solution word and number of attempts if successful,
               or (str, None) containing error message if unsuccessful
    """

    def log(message):
        if debug:
            print(message)

    def initialize_word_list():
        try:
            txt_file = "https://seleniumbase.github.io/cdn/txt/wordle_words.txt"
            word_string = requests.get(txt_file, timeout=3).text
            return ast.literal_eval(word_string)
        except Exception as e:
            return None

    def modify_word_list(word_list, word, letter_status):
        new_word_list = []
        correct_letters = []
        present_letters = []

        # Handle correct letters
        for i in range(len(word)):
            if letter_status[i] == "correct":
                correct_letters.append(word[i])
                new_word_list = [w for w in word_list if w[i] == word[i]]
                word_list = new_word_list
                new_word_list = []

        # Handle present letters
        for i in range(len(word)):
            if letter_status[i] == "present":
                present_letters.append(word[i])
                new_word_list = [w for w in word_list if word[i] in w and word[i] != w[i]]
                word_list = new_word_list
                new_word_list = []

        # Handle absent letters
        for i in range(len(word)):
            if letter_status[i] == "absent":
                if word[i] not in correct_letters and word[i] not in present_letters:
                    new_word_list = [w for w in word_list if word[i] not in w]
                else:
                    new_word_list = [w for w in word_list if word[i] != w[i]]
                word_list = new_word_list
                new_word_list = []

        return word_list

    try:
        # Initialize Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # New headless mode for Chrome
        chrome_options.add_argument("--window-size=1280,1024")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        # Initialize webdriver with options
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        # Open Wordle
        log("Opening Wordle...")
        driver.get("https://www.nytimes.com/games/wordle/index.html")

        # Handle initial popups and ads
        try:
            log("Handling cookie consent...")
            cookie_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.purr-blocker-card__button")))
            cookie_button.click()
        except TimeoutException:
            log("No cookie consent found")

        try:
            log("Looking for play button...")
            play_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='Play']")))
            play_button.click()
            log("Clicked play button")
        except TimeoutException:
            log("No play button found")

        try:
            log("Looking for close button...")
            close_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Close']")))
            close_button.click()
            log("Clicked close button")
        except TimeoutException:
            log("No close button found")

        # Initialize word list
        log("Initializing word list...")
        word_list = initialize_word_list()
        if not word_list:
            return "Failed to initialize word list", None

        # Start guessing
        random.seed()
        num_attempts = 0

        for attempt in range(6):
            num_attempts += 1
            if len(word_list) == 0:
                return "Today's word was not found in dictionary", None

            word = random.choice(word_list)
            log(f"\nAttempt {num_attempts}: Trying word '{word}'")

            # Input word
            for letter in word:
                button = f'button[data-key="{letter}"]'
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button))).click()
                time.sleep(0.1)  # Small delay between letters

            # Press enter
            log("Pressing enter...")
            enter_button = 'button[data-key="↵"]'
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, enter_button))).click()

            # Wait for animations to complete
            time.sleep(2)  # Wait for full animation sequence

            # Get results
            log("Getting tile results...")
            tiles = driver.find_elements(By.CSS_SELECTOR,
                                         f'div[class*="Row-module"]:nth-of-type({num_attempts}) div[class*="Tile-module"]')

            # Wait for all tiles to have a state
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                letter_status = []
                all_states_present = True
                for tile in tiles:
                    state = tile.get_attribute("data-state")
                    if not state or state == "empty" or state == "tbd":
                        all_states_present = False
                        break
                    letter_status.append(state)

                if all_states_present:
                    break

                retry_count += 1
                time.sleep(1)
                tiles = driver.find_elements(By.CSS_SELECTOR,
                                             f'div[class*="Row-module"]:nth-of-type({num_attempts}) div[class*="Tile-module"]')

            log(f"Tile states: {letter_status}")

            # Check if word is correct
            if letter_status.count("correct") == 5:
                log(f"Found the word: {word}")
                driver.quit()
                return word.upper(), num_attempts

            # Modify word list based on results
            word_list.remove(word)
            original_len = len(word_list)
            word_list = modify_word_list(word_list, word, letter_status)
            log(f"Word list reduced from {original_len} to {len(word_list)} words")

        # If we get here, we failed to solve in 6 attempts
        driver.quit()
        return f"Failed to solve. Final guess: {word.upper()}", None

    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        return f"An error occurred: {str(e)}", None


if __name__ == "__main__":
    result, attempts = solve_wordle(debug=True, headless=True)
    if attempts:
        print(f'\nSuccess! Word: "{result}" found in {attempts} attempts')
    else:
        print(f"\nError: {result}")