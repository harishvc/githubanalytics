#Source:https://docs.saucelabs.com/tutorials/python/#getting-started-with-python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

#Get Environment variables
if os.environ.get('TRAVIS_COMMIT') is not None:
    version = os.environ.get('TRAVIS_COMMIT')
else:
    version = ""
if os.environ.get('TRAVIS_BUILD_NUMBER') is not None:
    build = os.environ.get('TRAVIS_BUILD_NUMBER')
else:
    build = ""
    
desired_cap = {
    'platform': "Mac OS X 10.9",
    'browserName': "chrome",
    'version': version,
    'build': build,
}

#Sauce Labs
SauceLogin = os.environ['SauceLogin']
SauceAccessKey = os.environ['SauceAccessKey']

driver = webdriver.Remote(
   command_executor="http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (SauceLogin, SauceAccessKey),
   desired_capabilities=desired_cap)

# This is your test logic. You can add multiple tests here.
driver.implicitly_wait(10)
driver.get("http://localhost:5000")
assert "Ask GitHub" in driver.title
elem = driver.find_element_by_name("q")
elem.send_keys("trending now")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source

# This is where you tell Sauce Labs to stop running tests on your behalf.  
# It's important so that you aren't billed after your test finishes.
driver.quit()
