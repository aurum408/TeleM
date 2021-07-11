import asyncio
import time
import redis
import atexit
from ast import literal_eval
from selenium.common.exceptions import NoSuchElementException

from config import message_bots_warning_pattern
from telethon import TelegramClient


async def join_bot(tclient, bot_entity):
    dialogs = await tclient.get_dialogs()
    for d in dialogs:
        if d.name == bot_entity.first_name:
            break

    # subscribe_bot


def classify_bot_msg(msg):
    if msg.text.startswith(message_bots_warning_pattern):
        msg_type = "message bots task"

    elif msg.text.startswith("Sorry, there are no new ads available. 😟"):
        msg_type = "message bots no tasks yet"

    elif msg.text.startswith("Sorry, that is not a valid forwarded message."):
        msg_type = "message bots error"

    elif msg.text.startswith("You earned"):
        msg_type = "message bots success"

    else:
        raise NotImplementedError

    return msg_type


class TLSubscriber:
    def __init__(self, webdriver, telegram_client, max_mem_size: int = 10, max_try: int = 10, sleep: float = 1.):
        self.webdriver = webdriver
        self.tclient = telegram_client
        self.bot_uname = None
        self.bot_entity = None
        self.memory = []
        self.max_mem_size = max_mem_size
        self.max_try = max_try
        self.sleep = sleep
        self.job = None

    def set_bot(self, bot_username):
        if bot_username:
            self.bot_uname = bot_username
            self.bot_entity = self.tclient.get_entity(bot_username)

    async def start_and_forward(self,bot_ref):
        _entity = self.tclient.get_entity(bot_ref)
        await self.tclient.send_message(_entity, "/start params_string")
        n = 0
        while n < self.max_try:
            msgs = await self.tclient.get_messages(_entity)
            for msg in msgs:
                sender = await msg.get_sender()
                if sender.username == _entity.username:
                    await self.tclient.forward_messages(self.bot_entity, msg)

            await asyncio.sleep(self.sleep)
            n += 1

    def add2mem(self, data):
        if len(self.memory) < self.max_mem_size:
            self.memory.append(data)

        else:
            self.memory[0] = data

    async def message_bots_task_process(self, task_msg,):
        url = task_msg.buttons[0][0].url
        assert not (url in self.memory)

        if url in self.memory:
            return
        else:
            self.add2mem(url)
        self.webdriver.get(url)

        counter = 0
        _bot_ref = None

        while counter < self.max_try:
            try:
                _bot_ref = \
                    self.webdriver.find_element_by_xpath(".//div[@class='tgme_page_extra']").text
                break
            except NoSuchElementException:
                await asyncio.sleep(self.sleep)
                counter += 1
                continue

        if _bot_ref:
            await self.start_and_forward(_bot_ref)


    async def run_message_bots(self):
        while True:
            msgs = await self.tclient.get_messages(self.bot_entity)
            for msg in msgs:
                try:
                    msg_type = classify_bot_msg(msg)
                except NotImplementedError:
                    continue

                if msg_type == "message bots task":

                    await self.message_bots_task_process(msg)

                elif msg_type == "message bots no tasks yet":
                    await asyncio.sleep(5)

                elif msg_type == "message bots error":
                    await msg.buttons[1][1].click()

                elif msg_type == "message bots success":
                    pass

    async def start_command(self, command):
        await self.tclient.send_message(self.bot_entity, command)

        if command == "🤖 Message bots":
            job = await self.tclient.loop.run_until_complete(self.run_message_bots())
            self.job = job

    def stop(self):
        self.job.stop()


    def exit(self):
        self.stop()
        self.webdriver.quite()
        self.tclient.stop()


class TManager:
    def __init__(self, worker, redis, qname):
        self.redis = redis
        self.qname = qname
        self.worker = worker


    def process_task(self, task):
        task = literal_eval(task.decode())

        if task == "stop":
            self.worker.stop()

        elif task == "🤖 Message bots":
            self.worker.run_message_bots(self, task)

    def run(self):
        while True:
            task = self.redis.rpop(self.qname)
            if task:
                self.process_task(task)

    def exit(self):
        self.worker.exit()


worker = None
manager = None

def on_exit():
    try:
        worker.exit()
    except AttributeError:
        pass
    try:
        manager.exit()
    except AttributeError:
        pass

atexit.register(on_exit)

if __name__ == '__main__':
    from testconfig import bot_username, webdriver, api_id, api_hash, worker_name, headless

    from config import redis_config, chrome_config, firefox_config
    from webloader import build_firefox_driver, build_chrome_driver

    if webdriver == "chrome":
        driver = build_chrome_driver(chrome_config, headless)
    elif webdriver == "firefox":
        driver = build_firefox_driver(firefox_config, headless)
    else:
        driver = build_chrome_driver(chrome_config, headless)

    redis = redis.Redis(**redis_config)


    Id = (hash(time.time()) % 561) + 101

    name = worker_name + str(Id)

    tclient = TelegramClient('session_name', api_id, api_hash=api_hash)
    tclient.start()

    worker = TLSubscriber(driver, tclient)
    worker.set_bot(bot_username)

    manager = TManager(worker, redis, qname=name)

    manager.run()

    print("ok")









