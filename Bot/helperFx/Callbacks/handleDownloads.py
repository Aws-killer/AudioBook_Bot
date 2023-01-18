# import client and database
# create decorators
# implement the decorators
# add the downloading handler
#


""" 

Steps:
    - The user writes the book he wants. @
    - The query is sent to cloudflare, it populates the database (using a common transactionId). @ 
    - The bot sends the response. @
    - The user selects the response he/she wants. @
    - The bot triggers the download to start. @
    - The downloader is triggered from the plugins.@
    - The download start message is sent.@
    - The download progress message is sent.@
    - The download end message is sent.@
    - The file is processed and sent to the channel.
    -
"""

import pprint, ujson, asyncio, math
from urllib.parse import unquote

# from Bot import books_bot
from ..Schemas.dlSchema import (
    DownloadDb,
    init_database,
    async_session,
    select,
    addRow,
    commit,
    query,
)
import emoji
from ..messageTemplates import download_template


async def on_download_start(trigger, data):
    gid: str = data["params"][0]["gid"]
    uri: str = await trigger.getFiles(gid)
    # pprint.pprint(uri)
    # print(gid)
    # q = select(DownloadDb).where(DownloadDb.gid.ilike(f"%{gid}%"))
    # row: DownloadDb = await query(q, "one")
    # print(row)
    # print(row, "this is the correct ", row.title)
    # item = DownloadDb(
    #     title="xxx",
    #     author="author",
    #     page="asdasas",
    #     path="xx",
    #     gid=gid,
    #     links="asdsad",
    #     status="1",
    #     tl_data=ujson.dumps(
    #         {
    #             "user_id": None,
    #             "msg_id": None,
    #             "chat_id": None,
    #         }
    #     ),
    #     key_data=1,
    # )
    # await addRow(item)


async def on_download_complete(trigger, data):
    print("end..")
    gid: str = data["params"][0]["gid"]
    uri: str = await trigger.getFiles(gid)
    q = select(DownloadDb).where(DownloadDb.gid.ilike(f"%{gid}%"))
    row: DownloadDb = await query(q, "one")
    # print(row, gid)

    # item.status = 1
    # await addRow(item)


async def calcSize(client, gids):
    print("in")
    data = await asyncio.gather(*[client.tellStatus(gid) for gid in gids])
    # print("found all")
    result = {"completed": 0, "size": 0}
    for i in data:
        result["completed"] += int(i["completedLength"])
        result["size"] += int(i["totalLength"])
    # print(result)
    return result


async def download_status(client, booksBot):
    while True:
        q = select(DownloadDb).where(DownloadDb.download_status == -1)
        for item in await query(q):
            gids = ujson.loads(item.gid)
            print(item.chat_id, item.message_id)
            i = await booksBot.get_messages(int(item.chat_id), int(item.message_id))
            # print(i)
            # i = await booksBot.send_message(int(item.chat_id), "ok..")
            # print("asdasdasd")

            result = await calcSize(client, gids)
            # print(result)
            percentage = result["completed"] / result["size"] * 100
            if int(percentage) == 100:
                item.download_status = 0
                await asyncio.gather(
                   * [
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

            else:
                progress = "{0}{1} {2}%".format(
                    "".join(["▰" for i in range(math.floor(percentage / 5))]),
                    "".join(["▱" for i in range(20 - math.floor(percentage / 5))]),
                    round(percentage, 2),
                )

                await i.edit_text(f" {item.title} {percentage:.2f}% \n {progress}")
                await asyncio.sleep(1)
            # for gid in gids:
            #     x = await client.tellStatus(gid)
            #     # print(item.chat_id, gid)
            #     pprint.pprint(x)
            #     await i.edit_text(f"{gids.index(gid)}")
            #     await asyncio.sleep(0.5)
        await asyncio.sleep(1)
        print("end of loop")
