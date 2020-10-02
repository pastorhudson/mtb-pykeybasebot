from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome('../chromedriver/chromedriver', options=chrome_options)

driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
print(driver.title)
print(driver.name)
assert "No results found." not in driver.page_source
driver.close()