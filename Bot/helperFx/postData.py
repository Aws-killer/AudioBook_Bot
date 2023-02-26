import time, json, os
from urllib.parse import quote_plus
import aiohttp, re, pprint, asyncio
from pyrogram import Client
from fuzzywuzzy import fuzz
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from Bot import config_obj
from pyrogram.types import InputMediaPhoto, InputMediaAudio
from aria2p.utils import human_readable_bytes, human_readable_timedelta
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
    print('calling query')
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        [resp,gr_response] = await asyncio.gather(
            *[
                session.get(f"https://digitalbooks.api86.workers.dev/?query={query}"),
                session.get(
                    f"https://www.goodreads.com/book/auto_complete?format=json&q={query}"
                ),
            ]
        )
        print('getting response')
        [rez,gr_data]=await asyncio.gather(*[resp.json(),gr_response.json()])
        # print('getting response')
        
        # exit(0)
        print(rez,gr_data)
        if rez == {}:
            return [],gr_data

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
        ],gr_data


async def postData(query, client: Client = None):
    print(query["meta"])
    datas,goodData = await get_metadata(query["meta"])
        # print("this is datas *******************", datas)
    results = []
    
    best_result = {} #from digitalbooks.io
    best_good={ } # from goodreads

    for data in goodData:
        authors_score = max(
                [
                    fuzz.ratio(query["author"], data['author']['name'].lower()) / 100
                ]
            )
        title_score = fuzz.ratio(query["title"].lower(), data["bookTitleBare"].lower()) / 100
        results.append(sum([authors_score, title_score]))
    goodData=goodData[results.index(max(results))]
    results = []
    if datas!=[]:
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
        best_result=datas[results.index(max(results))]
    if best_result =={}:
        best_result['author'] = [goodData['author']['name']]
        best_result['title'] = goodData["bookTitleBare"]
    best_result['rating']=float(goodData['avgRating'])
    best_result['image']=goodData['imageUrl'].replace('SY75','SY400')
    best_result['author_image'] = goodData['author']["profileUrl"]
    # best_result['description'] = goodData["description"]

    return best_result

    # await client.send_audio(,)
