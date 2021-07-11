import os
import random

from config import message_bots_warning_pattern, visit_site_warning_pattern
from pyrogram import Client
from time import sleep
from selenium import webdriver
from pyrogram import filters
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import subprocess
from config import redis_config, chrome_config, firefox_config
from selenium.common.exceptions import TimeoutException
from webloader import build_chrome_driver, build_firefox_driver
from pyrogram.handlers import MessageHandler


def load_page(url, driver, delay, xpath=".//div[@class='tgme_page_extra']"):
    driver.get(url)
    try:
        condition = EC.presence_of_element_located((By.XPATH, xpath))
        new_bot_link = WebDriverWait(driver, delay).until(condition).text
    except TimeoutException:
        return
    return new_bot_link


def classify_bot_msg(msg):
    text = msg.text
    if text.startswith(message_bots_warning_pattern):
        msg_type = "message bots task"

    elif text.startswith("Sorry, there are no new ads available. 😟"):
        msg_type = "message bots no tasks yet"

    elif text.startswith("Sorry, that is not a valid forwarded message."):
        msg_type = "message bots error"

    elif text.startswith("You earned"):
        msg_type = "success"

    else:
        raise NotImplementedError

    return msg_type


def classify_visit_site_msg(msg):
    text = msg.text
    if text.startswith(visit_site_warning_pattern):
        msg_type = "task"

    elif text.startswith("You earned"):
        msg_type = "success"

    elif text.startswith("Please stay"):
        msg_type = "shit"

    else:
        raise NotImplementedError

    return msg_type


class TLSubscriber1:

    def __init__(self, max_mem_size: int = 10, max_try: int = 10, max_sleep: int = 10.):

        self.memory = []
        self.max_mem_size = max_mem_size
        self.max_try = max_try
        self.max_sleep = max_sleep

        self.bot = None
        self.bot_chat_id = None
        self.command = None
        self.app = None
        self.webdriver = None



    def start_and_forward(self, new_bot_url, old_chat_id):
        print("ok")
        assert new_bot_url
        msg = self.app.send_message(new_bot_url, "/start")
        chat_id = msg.chat.id

        # for i in range(self.max_try):
        sleep(self.max_sleep)
        res = app.get_history(chat_id)[0]
        if app.get_me() != res.from_user:
            app.forward_messages(old_chat_id, chat_id, res.message_id)

    def do_visit_site_task(self, msg):
        print("processing")

        try:
            msg_type = classify_visit_site_msg(msg)
        except NotImplementedError:
            return

        chat_id = msg.chat.id

        if msg_type == "task":
            url = msg.reply_markup.inline_keyboard[0][0].url

            # assert url not in self.memory, app.request_callback_answer(
            #         chat_id=chat_id,
            #         message_id=msg.message_id,
            #         callback_data=msg.reply_markup.inline_keyboard[1][1].callback_data
            #     )

            #self.webdriver.get(url)
            os.system("open -a 'Google Chrome' {}".format(url))
            sleep(random.randint(30, 45))
            # self.webdriver.quit()
            # self.webdriver = build_chrome_driver(chrome_config, headless=False)

            self.memory.append(url)

            if len(self.memory) >= self.max_mem_size:
                self.memory = self.memory[2:]

            # self.webdriver.clear()


        #else:



    def do_message_bot_task(self, msg):
        print("processing")
        try:
            msg_type = classify_bot_msg(msg)
        except NotImplementedError:
            return

        chat_id = msg.chat.id
        print(msg_type)

        if msg_type == "message bots task":

            url = msg.reply_markup.inline_keyboard[0][0].url

            if url not in self.memory:
                new_bot_url = load_page(url, self.webdriver, delay=10)

                try:
                    self.start_and_forward(new_bot_url, chat_id)
                except AssertionError:
                    pass
                self.memory.append(url)
                if len(self.memory) >= self.max_mem_size:
                    self.memory = self.memory[2:]

            else:
                app.request_callback_answer(
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    callback_data=msg.reply_markup.inline_keyboard[1][1].callback_data
                )


        elif msg_type == "message bots no task yet":
            pass

        if msg_type == "message bots error":
            #click skip button
            app.request_callback_answer(
                chat_id=chat_id,
                message_id=msg.message_id,
                callback_data=msg.reply_markup[1][1].callback_data
            )

        if msg_type == "message bots success":
            app.send_message(self.bot, self.command)


    def start_command(self, command):

        self.command = command
        #handler = MessageHandler(self.process_bot_msg, filters.chat(self.bot))
        #self.app.add_handler(handler)
        #self.app.run()
        msg = self.app.send_message(self.bot, self.command)
        self.bot_chat_id = msg.chat.id


    # def run(self, command):
    #     self.start_command(command)

    def run(self, command):
        self.start_command(command)

        while True:
            msg = self.app.get_history(self.bot_chat_id)[0]
            # sleep(random.randint(0, self.max_sleep))

            if command == "🤖 Message bots":
                self.do_message_bot_task(msg)

            elif command == "/visit":

                try:
                    self.do_visit_site_task(msg)
                except AssertionError:
                    continue




if __name__ == '__main__':
    from testconfig import api_id, api_hash, bot_username

    #command = "🤖 Message bots"
    command = "/visit"
    # driver = build_chrome_driver(chrome_config, headless=False)
    worker = TLSubscriber1()

    # worker.webdriver =  driver
    worker.bot = bot_username

    app = Client("new_session", api_id, api_hash)

    # handler = MessageHandler(worker.process_bot_msg, filters.chat(worker.bot))
    # app.add_handler(handler)
    app.start()


    # app.start()

    worker.app = app
    # worker.start_command(command)
    worker.run(command)
    # app.send_message("@Dogecoin_click_bot", "/start")
    #app.run()
    print("ok")


