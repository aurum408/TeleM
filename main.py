import asyncio
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import FloodWaitError
import requests
from lxml import etree
import time
import asyncio

from webloader import get_bot_name

api_id = 6559151
api_hash = '5da6840ec7400f1cebb16e2c44898408'
BOT = "@Dogecoin_click_bot"
BOT_NAME = "DOGE Click Bot"
button = '✉️ Message bot'
phone='79650701435'

#@BitcoinClick_bot

client = TelegramClient('session_name', api_id, api_hash)

parser = etree.HTMLParser()

LAST_URL = None

warning_pattern = "⚠️ WARNING: The following is a third party advertisement. " \
                  "Do not trust anything that promises to make you money. " \
                  "Use the following bot at your own risk."


def build_firefox_driver(executable_path: str, headless: bool = True):
    options = webdriver.FirefoxOptions()
    options.headless = headless
    driver = webdriver.Firefox(executable_path=executable_path, options=options)
    return driver


def build_fchrome_driver(executable_path: str, headless: bool = True):
    options = webdriver.ChromeOptions()
    options.headless = headless
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    return driver



def classify_bot_msg(msg):
    if msg.text.startswith(warning_pattern):
        msg_type = "task"

    elif msg.text.startswith("Sorry, there are no new ads available. 😟"):
        msg_type = "no tasks yet"

    elif msg.text.startswith("Sorry, that is not a valid forwarded message."):
        msg_type = "error"

    elif msg.text.startswith("You earned"):
        msg_type = "success"

    else:
        raise NotImplementedError

    return msg_type



def filter_msg(message):
    time.sleep(0.3)
    try:
        if (message.buttons[0][0].text == button):
            return True
        else:
            return False
    except TypeError:
        return False
    except AttributeError:
        return False

def not_filter_msg(message):
    return not filter_msg(message)

async def wait_res(client, entity):

    while True:
        msgs = await client.get_messages(entity)
        for m in msgs:
            sender = await m.get_sender()
            if sender.username == entity.username:

                await client.forward_messages(BOT, m)
                break


async def process_bot_dialog(client, bot_entity):
    iter = 0
    n = 10
    while iter < n:
        msg = await client.get_messages(bot_entity)
        for m in msg:
            sender = await m.get_sender()
            if sender.username == bot_entity.username:
                await m.forward_to(BOT)

                break
        iter += 1


async def process_bot_msg(msg):
    global LAST_URL
    if filter_msg(msg):
        url = msg.buttons[0][0].url
        if url != LAST_URL:
            _bot_ref = get_bot_name(url)

            if _bot_ref == None:
                return

            _bot_entity = await client.get_entity(_bot_ref)
            _bot_name = _bot_entity.first_name

            await client.send_message(_bot_entity, '/start params_string')
            dialogs = await client.get_dialogs()

            for d in dialogs:
                if d.name == _bot_name:
                    await process_bot_dialog(client, _bot_entity)

            LAST_URL = url

        else:
            await msg.buttons[1][1].click()
    else:
        await client.send_message(BOT, "🤖 Message bots")




async def run1(client):

    # await client.send_message(BOT, "🤖 Message bots")
    res = await client.get_messages(BOT)

    for msg in res:
        await process_bot_msg(msg)


async def start_and_forward(client, bot_ref, home_bot_entity, max_try=10):
    _entity = client.get_entity(bot_ref)
    await client.send_message(_entity, "/start params_string")

    n = 0

    while n < max_try:
        msgs = await client.get_messages(_entity)
        for msg in msgs:
            sender = await msg.get_sender()
            if sender.username == _entity.username:
                await client.forward_messages(home_bot_entity, msg)
                break

        n+=1







async def process_task(task_msg, client, driver):
    url = task_msg.buttons[0][0].url
    if url == LAST_URL:
        task_msg.buttons[1][1].click()
    else:
        driver.get(url)
        try:
            _bot_ref = driver.find_element_by_xpath(".//div[@class='tgme_page_extra']").text
        except NoSuchElementException:
            return





async def run2(client, driver, bot):

    res = await client.get_messages(bot)
    for msg in res:
        try:
            msg_type = classify_bot_msg(msg)
        except NotImplementedError:
            continue

        if msg_type == "task":
            pass
        elif msg_type == "no tasks yet":
            pass
        elif msg_type == "error":
            pass
        elif msg_type == "success":
            pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    driver = "chrome"
    client.start()

    bot_entity = client.get_entity(BOT)

    # client.add_event_handler(handler1, event=events.NewMessage(pattern=not_filter_msg))
    # client.add_event_handler(handler, event=events.NewMessage(pattern=filter_msg))
    #while True:
    # client.run_until_disconnected()

    while True:
        client.loop.run_until_complete(run1(client))
    # client.run_until_disconnected()
        #

    #
    # me = await client.get_me()
    # # me = await client.get_me()
    # print(me.username)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
