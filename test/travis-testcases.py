#http://selenium-python.readthedocs.org/en/latest/getting-started.html

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

driver = webdriver.Firefox()
driver.get("http://localhost:5000")
assert "Ask GitHub" in driver.title
elem = driver.find_element_by_name("q")
elem.send_keys("trending now")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()
