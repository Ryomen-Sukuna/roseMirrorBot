from os import getenv, listdir
from logging import basicConfig, INFO, info

from telethon import TelegramClient
from pymongo import MongoClient
from importlib import import_module

basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=INFO,
    filename="logs.log",
    filemode="a",
)

API_KEY = int(getenv('API_KEY', 6))
API_HASH = getenv('API_HASH')
TOKEN = getenv('TOKEN')
MONGO_URL = getenv('MONGO_URL')
OWNER_ID = int(getenv('OWNER_ID', 0))

db = MongoClient(MONGO_URL)

bot = TelegramClient("bot", API_KEY, API_HASH,
                     device_model="iPhone XS", system_version="12.0",)


def load_modules():
    for module in listdir("modules"):
        if module.endswith(".py"):
            import_module("modules." + module[:-3])
            info("Loaded module: " + module)


def setup_aria2():
    pass
