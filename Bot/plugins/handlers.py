from pyrogram.types import *
import emoji, time, pprint
from pyrogram import Client, filters
from lxml import html
from Bot.helperFx.Schemas.dlSchema import (
    DownloadDb,
    IndexDb,
    deleteRow,
    # init_database,
    async_session,
    select,
    addRow,
    commit,
    query,
)
from Bot.helperFx.messageTemplates import audio_item
from Bot.helperFx.onlineBooks import Fla, Get_Links
from Bot.helperFx.messageTemplates import greeting_template, download_template
from Bot import config_obj
from ..helperFx.elasticMongo import quickSearch
from Bot import _downloader
import logging
import uuid, asyncio, ujson, json


def divide_chunks(l, n):
    items = []

    for i in range(0, len(l), n):
        items.append(l[i : i + n])
    return items


async def clearDb(item):
    # clear the db
    q = select(IndexDb).where(IndexDb.transactionId == item.transactionId)
    rows = await query(q)
    for i in rows:
        await deleteRow(i)


@Client.on_message(filters.command(["start"], prefixes="/"))
async def handle_start(_, message: Message):
    await message.reply_text(
        greeting_template.render(
            **{
                "user_name": f"{message.from_user.first_name}",
                "bot_name": config_obj["telegram"]["bot_name"],
            }
        )
    )


@Client.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    Download_Client = _downloader.get()
    user_id = callback_query.from_user.id
    data = callback_query.data
    await client.delete_messages(
        callback_query.message.chat.id,
        [
            callback_query.message.id,
        ],
    )

    # print(data)
    q = select(IndexDb).where(IndexDb.id == data)
    item: IndexDb = await query(q, "one")
    data = await quickSearch(item.page.split("/")[-2])


    q = select(DownloadDb).where(DownloadDb.page == item.page.split("/")[-2])
    copy: DownloadDb = await query(q, "one")
 

    print(data)
    if data != None or copy:
        await clearDb(item)
        pprint.pprint(data)

        return
    print(item.page.split("/")[-2])

    links = await Get_Links(item.page)
    item.title = html.fromstring(item.title).text
    downloadItem = DownloadDb(
        author=item.author,
        title=item.title,
        page=item.page.split("/")[-2],
        chat_id=callback_query.message.chat.id,
    )

    # print(links[0].split("/")[-2], item.title)

    # start the download
    downloadGids = await asyncio.gather(
        *[
            Download_Client.addUri(
                [link],
                options={"dir": f"./Downloads/{item.title}"},
            )
            for link in links
        ]
    )
    print("sending message..")
    msg = await client.send_message(
        chat_id=callback_query.message.chat.id,
        text=download_template.render(
            **{
                "name": item.title,
                "emoji": emoji.emojize(":stopwatch:"),
                "state": True,
            }
        ),
        reply_markup=None,
    )
    downloadItem.message_id = msg.id
    downloadItem.gid = ujson.dumps(downloadGids)
    # print(downloadItem.gid)
    await addRow(downloadItem)
    await clearDb(item)


@Client.on_message(filters.private & filters.regex("^magnet:?.*"))
async def handle_magnet(_, message: Message):
    Download_Client = _downloader.get()
    link = message.text
    x = await message.reply_text("got magnet")
    downloadItem = DownloadDb(
        author="asdas",
        title="magnet",
        chat_id=message.chat.id,
    )
    gid = await Download_Client.addUri(
        [link],
        options={"dir": f"./Downloads/Torrent"},
    )
    downloadItem.message_id = x.id
    downloadItem.gid = ujson.dumps([gid])
    await addRow(downloadItem)
    # await message.reply_text('got magnet')


@Client.on_message(filters.private)
async def handle_query(_, message: Message):
    message.text
    ABooks = await Fla(message.text)
    if not ABooks:
        await message.reply_text(
            f" No result for {message.text} 🤷🏻 ",
        )
        return
    response = ""
    rows = []
    _id = str(uuid.uuid4())[:8]
    for book in ABooks:
        item = IndexDb(
            id=str(uuid.uuid4())[:8],
            transactionId=_id,
            page=book["url"],
            title=book["title"],
            author=book["author"],
            tlData=ujson.dumps(
                {
                    "user_id": message.from_user.id,
                    "msg_id": message.id,
                    "chat_id": message.chat.id,
                }
            ),
        )
        # print(item)
        await addRow(item)

        response = response + audio_item.render(
            **{
                "number": emoji.emojize(f":keycap_{ABooks.index(book)+1}:"),
                "Title": book["title"],
                "Author": book["author"],
            }
        )

        rows.append(
            InlineKeyboardButton(
                text=emoji.emojize(f":keycap_{ABooks.index(book)+1}:"),
                callback_data=item.id,
            )
        )

    await message.reply_text(
        response, reply_markup=InlineKeyboardMarkup(divide_chunks(rows, 3))
    )
