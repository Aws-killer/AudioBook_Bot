import os, contextvars, configparser
from pyrogram import Client

# Read config.ini file
config_obj = configparser.ConfigParser()
print(f"{os.getcwd()}/Bot/config.ini")
config_obj.read(f"{os.getcwd()}/Bot/config.ini")

bot_config = config_obj["pyrogram"]

books_bot = Client(
    name="books_bots",
    bot_token=bot_config["bot_token"],
    api_id=bot_config["api_id"],
    api_hash=bot_config["api_hash"],
    plugins={"root": "Bot/plugins"},
)


_downloader = contextvars.ContextVar("")
