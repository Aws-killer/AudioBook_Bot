import aiohttp, re, pprint, asyncio
from bs4 import BeautifulSoup

pattern = 'href="(.*)">\s{1,}(\w.*) &#8211; (\w.+) Audiobook Free &raquo;'
request_data = {
    "url": "https://fulllengthaudiobooks.com/wp-admin/admin-ajax.php",
    "headers": {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,sw;q=0.8,la;q=0.7,fr;q=0.6",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    },
}


async def Get_Links(page_link, check=True):

    async with aiohttp.ClientSession() as session:
        resp = await session.get(page_link)
        page = await resp.text()
        soup = BeautifulSoup(page, "html.parser")

    pages = soup.findAll("a", attrs={"class": "post-page-numbers"})
    links = []
    if check and pages:
        for page in pages:
            links.extend(await Get_Links(page.attrs["href"], check=False))
        return links

    return [i.attrs["src"].split("?")[0] for i in soup.findAll("source")]


async def Fla(query):

    async with aiohttp.ClientSession() as session:

        data = {
            "s": f"{query}",
            "action": "searchwp_live_search",
            "swpengine": "default",
            "swpquery": f"{query}",
            "origin_id": "0",
        }

        # async with session.post(
        #     request_data["url"], data=data, headers=request_data["headers"]
        # ) as resp:
        async with session.get(
            f"https://test-books-scraper.api86.workers.dev/?book={query}"
        ) as resp:

            string = await resp.text()

            result = [
                {"url": i[0], "author": i[1], "title": i[2]}
                for i in re.findall(pattern, string)
            ]
            return result
