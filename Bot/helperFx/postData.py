import time, json, os
import aiohttp, re, pprint, asyncio
from pyrogram import Client
from fuzzywuzzy import fuzz
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from Bot import config_obj
from pyrogram.types import InputMediaPhoto, InputMediaAudio
from aria2p.utils import human_readable_bytes, human_readable_timedelta
from Bot.helperFx.Schemas.dlSchema import session, DownloadDb
from six.moves.urllib.request import urlretrieve


def download_file(file_url, name=None):
    file_output_path = os.path.join("./Downloads", name + ".jpeg")
    filename, _ = urlretrieve(file_url, file_output_path)
    return file_output_path


async def upload_files(id, client: Client):
    _download: DownloadDb = session.query(DownloadDb).filter_by(id=id).first()
    print(json.loads(_download.links))
    # client.send_media_group(
    #     chat_id=config_obj["telegram"],
    #     media=[InputMediaPhoto("photo1.jpg"), []],
    # )
    # pass


async def upload_book(id):
    # upload all the files async
    #
    #
    pass


async def get_metadata(query):

    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        resp = await session.get(
            f"https://digitalbooks.api86.workers.dev/?query={query}"
        )
        rez = await resp.json()
        return [
            {
                "image": i["Images"]["Primary"]["Medium"]["URL"],
                "genres": [
                    j["ContextFreeName"] for j in i["BrowseNodeInfo"]["BrowseNodes"]
                ],
                "title": i["ItemInfo"]["Title"]["DisplayValue"],
                "authors": [
                    a["Name"]
                    for a in i["ItemInfo"]["ByLineInfo"]["Contributors"]
                    if a["Role"] == "Author"
                ],
                "locale": i["ItemInfo"]["Title"]["Locale"],
            }
            for i in rez["SearchResult"]["Items"]
        ]


async def postData(query, client: Client = None):
    print(query["meta"])
    datas = await get_metadata(query["meta"])
    results = []
    for data in datas:

        # print("-" * 100)
        # pprint.pprint(data)
        authors_score = max(
            [
                fuzz.ratio(query["author"], author.lower()) / 100
                for author in data["authors"]
            ]
        )
        title_score = fuzz.ratio(query["title"].lower(), data["title"].lower()) / 100
        results.append(sum([authors_score, title_score]))
        # print(
        #     , data["title"], authors_score, title_score
        # )
    return datas[results.index(max(results))]
    # await client.send_audio(,)


# asyncio.run(
#     postData(
#         {
#             "meta": "CHRISTINA LAUREN  DATING YOU  HATING You",
#             "title": "DATING YOU HATING You",
#             "author": "CHRISTINA LAUREN",
#         }
#     )
# )
