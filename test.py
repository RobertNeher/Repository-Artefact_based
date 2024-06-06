import src.settings as settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient(settings.uri, server_api=ServerApi('1'))
wiHistoryCollection = client[settings.dbName].get_collection(settings.workItemHistoryCollection)

rev = wiHistoryCollection.find_one({"revision": {"$gte": 0}})

print(rev["revision"])
