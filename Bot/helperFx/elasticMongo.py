import pprint
from Bot import config_obj

from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(hosts=[config_obj["elasticsearch"]["url"]])
