import settings as settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING

def initializeRepo():
    client = MongoClient(settings.uri, server_api=ServerApi('1'))

    # create database and work item collection
    if not settings.dbName in client.list_database_names():
        db = client[settings.dbName]
    else:
        db = client.get_database(settings.dbName)

    if not settings.workItemCollection in db.list_collection_names():
        wiCollection = db[settings.workItemCollection]
        db.drop_collection(settings.baselineCollection)
    else:
        wiCollection = db.get_collection(settings.workItemCollection)
        db.get_collection(settings.workItemHistoryCollection).delete_many({})

    # create index
    if not settings.wiIndex in wiCollection.list_indexes():
        wiCollection.create_index(['projectID', 'workItemID'], name=settings.wiIndex)

    # empty workItemCollection
    wiCollection.delete_many({})

    # reset revisions store
    print("Reset revisions store and baselines")

    if not settings.baselineCollection in db.list_collection_names():
        baselines = db[settings.baselineCollection]
        db.drop_collection(settings.baselineCollection)

    baselines = db.get_collection(settings.baselineCollection)
    baselines.delete_many({})

    revision = client[settings.dbName].get_collection(settings.revisionsCollection)
    revision.delete_many({})
    revision.insert_one({"revision": 0})

    if not settings.baselineIndex in baselines.list_indexes():
        baselines.create_index({'revision': DESCENDING}, name=settings.baselineIndex)


if __name__ == "__main__":
    initializeRepo()