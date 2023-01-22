""" 
Steps:
    - The user writes the book he wants. @
    - The query is sent to cloudflare, it populates the database (using a common transactionId). @ 
    - The bot sends the response. @
    - The user selects the response he/she wants.@
    - The bot triggers the download to start. @
    - The downloader is triggered from the plugins.@
    - The download start message is sent.@
    - The download progress message is sent.@
    - The download end message is sent.@
    - The file is processed and sent to the channel.@
    -
"""

import pprint, ujson, asyncio, math, os, shutil
import emoji, re, uuid
from Bot.helperFx.elasticMongo import quickSearch
from pyrogram.errors import FloodWait
from aioaria2 import Aria2WebsocketClient
from urllib.parse import unquote
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from Bot import config_obj

# from Bot import books_bot
from ..Schemas.dlSchema import (
    DownloadDb,
    init_database,
    async_session,
    select,
    addRow,
    deleteRow,
    commit,
    query,
)
from ..elasticMongo import add_2index
from ..messageTemplates import download_template, post_template
from ..postData import postData, download_file
from pyrogram.types import InputMediaPhoto, InputMediaAudio, InputMediaDocument

clean = re.compile("[^a-zA-Z] ")


def divide_chunks(l, n):
    items = []

    for i in range(0, len(l), n):

        items.append(l[i : i + n])
    return items


async def ubuntu_cleaner(folder):
    try:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        else:
            os.remove(folder)
        subprocess.call("apt-get clean", shell=True)
    except:
        pass


async def on_download_start(trigger, data):
    gid: str = data["params"][0]["gid"]
    uri: str = await trigger.getFiles(gid)


async def on_download_complete(trigger: Aria2WebsocketClient, data):
    gid: str = data["params"][0]["gid"]
    status = await trigger.tellStatus(gid)

    if "followedBy" in status:
        q = select(DownloadDb).where(DownloadDb.gid.ilike(f"%{gid}%"))
        item: DownloadDb = await query(q, qtype="one")
        item.gid = ujson.dumps(status["followedBy"])
        item.download_status = -1
        await addRow(item)


async def calcSize(client, gids):
    data = await asyncio.gather(*[client.tellStatus(gid) for gid in gids])
    result = {"completed": 0, "size": 0}
    for i in data:
        result["completed"] += int(i["completedLength"])
        result["size"] += int(i["totalLength"])
    return result


async def uploadFiles(client, booksBot):
    while True:

        q = select(DownloadDb).where(DownloadDb.download_status == 0)
        for item in await query(q):
            item: DownloadDb
            _meta = await postData(
                {
                    "meta": clean.sub(" ", f"{item.title} {item.author}"),
                    "title": item.title,
                    "author": item.author,
                }
            )

            # upload and get the message_ids
            parent = f"{os.getcwd()}/Downloads/{item.title}"
            _files = []

            for directory, dirnames, filenames in os.walk(parent):
                # print(filenames)

                _files.extend(
                    [os.path.join(parent, filename) for filename in filenames]
                )
                # print(filenames)
            _files = sorted(_files)
            audio_media = [
                InputMediaAudio(
                    media=i,
                    duration=extractMetadata(createParser(i)).get("duration").seconds,
                    title=f"{item.title} {_files.index(i)+1} ",
                    performer=item.author,
                    thumb=download_file(_meta["image"], name=item.title),
                )
                for i in _files
            ]
            while True:
                #
                try:
                    #
                    await booksBot.send_photo(
                chat_id=int(config_obj["telegram"]["archive_id"]),
                photo=_meta["image"].replace("SL160", "SL300"),
                caption=post_template.render(**_meta),
            )
                    break
                except FloodWait as e:
                    asyncio.sleep(e.value)


            msgs = []
            for batch in divide_chunks(audio_media, 8):
                pprint.pprint(batch)
                while True:
                    try:
                        x = await booksBot.send_media_group(
                            chat_id=config_obj["telegram"]["archive_id"],
                            media=batch,
                        )
                        msgs.extend([i.id for i in x])

                        await asyncio.sleep(1)
                        break
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
            _meta["ids"] = msgs
            _meta["slug"] = item.page
            await asyncio.gather(*[add_2index(body=_meta), deleteRow(item)])
            await ubuntu_cleaner(parent)


async def download_status(client, booksBot):
    while True:
        
        print("re loop")
        q = select(DownloadDb).where(DownloadDb.download_status == -1)
        for item in await query(q):
            item: DownloadDb
            gids = ujson.loads(item.gid)
            print(item.chat_id, item.message_id)
            i = await booksBot.get_messages(int(item.chat_id), int(item.message_id))
            result = await calcSize(client, gids)
            if result["size"] != 0:
                percentage = result["completed"] / result["size"] * 100
            else:
                percentage = 0
            if int(percentage) == 100:
                
                item.download_status = 0
                try:

                    #
                    await asyncio.gather(
                    *[
                        addRow(item),
                        i.edit_text(
                            download_template.render(
                                **{
                                    "name": unquote(item.title),
                                    "emoji": emoji.emojize(":check_mark_button:"),
                                    "state": False,
                                }
                            ),
                            reply_markup=None,
                        ),
                    ]
                )
                except:
                    
                    pass

            else:
                progress = "{0}{1} {2}%".format(
                    "".join(["▰" for i in range(math.floor(percentage / 5))]),
                    "".join(["▱" for i in range(20 - math.floor(percentage / 5))]),
                    round(percentage, 2),
                )
                reply = f" {item.title} {percentage:.2f}% \n {progress}"
                if item.progress != percentage:
                    try:
                        #
                        await i.edit_text(reply)
                    except:
                        pass   

                item.progress = percentage
                await addRow(item)
                await asyncio.sleep(1)

        await asyncio.sleep(6)
