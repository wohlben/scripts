import os
from time import sleep
from downloads_db import DBConn
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


user = os.environ['oid']
password = os.environ['opw']
db = DBConn()

# force pdf downloads
chrome_profile = webdriver.ChromeOptions()
profile = {
    "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    "download.default_directory": ".",
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
chrome_profile.add_experimental_option("prefs", profile)

# chromedriver isnt in path
driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_profile)

# start
driver.get("https://login.o2online.de/auth/login?goto=https://www.o2online.de:443/ecare/")

if "o2 Login" in driver.title:
    print('logging in')
    login_element = driver.find_element_by_id("IDToken1")
    login_element.send_keys(user)
    password_element = driver.find_element_by_id("IDToken2")
    password_element.send_keys(password)
    submit = driver.find_element_by_xpath('//button[@type="submit"]')
    submit.click()

    sleep(5)  # TODO: Fix it with wait until available...

    driver.get("https://www.o2online.de/ecare/?0&contentId=rechnung/uebersicht")

    sleep(6)  # TODO: Fix it with wait until available

    bills = driver.find_elements_by_xpath('//div[@class="panel panel-action"]')
    print("found {} news".format(len(bills)))

    for element in bills:
        date = element.find_element_by_xpath('div/div/span[not(contains(text(), "Aktuelle "))]')
        title = "Rechnung vom {}".format(date.text)

        if db.has_entry(site="o2", name=title) is False:
            print("Found {}".format(title))
            url = element.find_element_by_xpath(".//a")
            url.click()
            db.add_download(site="o2", name=title, uri=url.get_property('href'))

    print('byebye')
    db.bye()
    driver.close()
