from pyrogram import Client
import configparser, asyncio
import os, contextvars
from .helperFx.Callbacks.handleDownloads import (
    on_download_start,
    on_download_complete,
    download_status,
)
from .helperFx.Schemas.dlSchema import init_database
from Bot import _downloader, books_bot
from Bot.helperFx.downloading import download_pool

loop = asyncio.get_event_loop()


async def get_download_client():
    print(_downloader)
    return _downloader


async def main():
    x = await download_pool()
    x.onDownloadStart(on_download_start)
    x.onDownloadComplete(on_download_complete)

    # await download_status(x)
    _downloader.set(x)
    await init_database()
    print(_downloader)
    asyncio.run_coroutine_threadsafe(download_status(x, books_bot), loop)
    await books_bot.start()


if __name__ == "__main__":

    loop.create_task(main())
    loop.run_forever()
