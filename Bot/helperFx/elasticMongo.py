import pprint, uuid
from Bot import config_obj
from pyrogram.types import Message
from elasticsearch import AsyncElasticsearch

elastic_config = config_obj["elasticsearch"]
es = AsyncElasticsearch(hosts=[elastic_config["url"]])


# Fast five
async def add_2index(body: dict):
    resp = await es.index(
        index=elastic_config["index"], id=str(uuid.uuid4())[:8], body=body
    )
    print(resp)


async def quickSearch(slug):
    body = {"query": {"term": {"slug.keyword": {"value": slug}}}}
    resp = await es.search(
        index=elastic_config["index"],
        body=body,
        size=1,
    )
    if resp["hits"]["total"]["value"] > 0:
        return resp["hits"]["hits"][0]
