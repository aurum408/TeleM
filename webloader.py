import selenium
from selenium import webdriver
import atexit
import redis
import re

task_q_name = "tele_m"
redis_config = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
    "password": None
}

firefox_config = {"executable_path": "/Users/anastasia/PycharmProjects/TeleM/drivers/geckodriver",}
chrome_config = {
    "executable_path": "/Users/anastasia/PycharmProjects/TeleM/drivers/chromedriver"
}

from lxml import etree


def build_firefox_driver(config=None, headless=True):
    if config is None:
        config = firefox_config
    options = webdriver.FirefoxOptions()
    options.headless = headless
    driver = webdriver.Firefox(**config, options=options)

    return driver


def build_chrome_driver(config=None, headless=True):
    if config is None:
        config = chrome_config
    options = webdriver.ChromeOptions()
    options.headless = headless
    driver = webdriver.Chrome(**config, options=options)

    return driver


def get_bot_name(url):
    options = webdriver.FirefoxOptions()
    options.headless = False
    driver = webdriver.Firefox(**firefox_config, options=options)
    driver.get(url)
    driver.maximize_window()
    page_source = driver.execute_script("return document.documentElement.outerHTML;")

    parser = etree.HTMLParser()
    tree = etree.fromstring(page_source, parser)
    bot_name = tree.find(".//div[@class='tgme_page_extra']")
    if bot_name:

        bot_name = re.sub(r"[\n\t\s]*", "", bot_name.text)

    driver.quit()

    return bot_name



