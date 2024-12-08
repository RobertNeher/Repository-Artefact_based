import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING

import src.misc.settings as settings

def confirmation() -> bool:
    """
    Ask user to confirm initialization by entering Y or N (case-insensitive).
    :return: True if the answer is Y.
    """
    answer = ""

    while answer not in ["y", "n"]:
        answer = input("Please confirm initialization of repository [Y/N]? ").lower()
    return answer == "y"

def initializeRepo() -> None:
    if not confirmation():
        sys.exit(0)

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

    if not settings.workItemHistoryCollection in db.list_collection_names():
        wiHistoryCollection = db.create_collection(settings.workItemHistoryCollection)
    else:
        wiHistoryCollection = db[settings.workItemHistoryCollection]

    # create index
    if not settings.wiHistoryIndex in wiHistoryCollection.list_indexes():
        wiHistoryCollection.create_index(["workItemID", {"revision", DESCENDING}], unique=True)

    # empty workItemCollection
    wiCollection.delete_many({})
    print("Work item store erased.")

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

    print("Initialization finished")

if __name__ == "__main__":
    initializeRepo()