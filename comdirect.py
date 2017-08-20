import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

user = os.environ['bid']
password = os.environ['bpw']


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
driver.get("https://kunde.comdirect.de/lp/wt/login")
loginpage = driver.find_element_by_css_selector("h1.headline")

if loginpage.text == "Ihr persönlicher Bereich":
    print('logging in')
    login_element = driver.find_element_by_id("param1Input")
    login_element.send_keys(user)
    password_element = driver.find_element_by_id("param3Input")
    password_element.send_keys(password)
    submit = driver.find_element_by_id("loginAction")
    submit.click()

    driver.find_element_by_xpath('//div[@class="col__content"]')
    print('authentication successfull')

    driver.get("https://kunde.comdirect.de/itx/posteingangsuche")
    news = driver.find_elements_by_xpath('//tbody//a/span')
    print("found {} news".format(len(news)))

    for element in news:
        if element.text.startswith("Finanzreport"):
            url = element.find_element_by_xpath("..")
            print("Found {}".format(element.text))
            url.click()

    if len(news) > 0:
        print('marking everything as read')
        driver.find_element_by_xpath('//label[text()="Alle auswählen"]/../input').click()
        driver.find_element_by_xpath('//*[text()="Ablegen"]/..').click()

    print('byebye')
    driver.close()
