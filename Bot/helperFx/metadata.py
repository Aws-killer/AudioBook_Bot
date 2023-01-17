import aiohttp, re, pprint, asyncio


async def get_metadata(query):

    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        resp = await session.get(
            f"https://digitalbooks.api86.workers.dev/?query={query}"
        )
        rez = await resp.json()

        for i in rez["SearchResult"]["Items"]:
            data = [
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
        pprint.pprint(data)


# asyncio.run(get_metadata("DANTE ALIGHIERI – THE DEVINE COMEDY"))
