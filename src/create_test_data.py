import random

from pymongo import DESCENDING
import settings as settings
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

wiIndex = "workItemIndex"
baselineIndex = "baselineIndex"

def createTestData():
    # Create a new client and connect to the server
    projectID = 1
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
    if not wiIndex in wiCollection.list_indexes():
        wiCollection.create_index(['projectID', 'workItemID'], name=wiIndex)

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

    if not baselineIndex in baselines.list_indexes():
        baselines.create_index({'revision': DESCENDING}, name=baselineIndex)

    # create test data

    print('Creation started: {}'.format(datetime.now()))

    wordCount = len(settings.textBlob.split(' '))
    data = []

    for rec in range(wordCount):
        dt = datetime.now()
        size = random.randint(0, wordCount)
        data.append({
            'projectID': projectID,
            'created': dt,
            'status': 'open',
            'createdBy': 'BHC',
            'title': 'Dataset {} as of {}'.format(rec, dt.strftime("%d. %b %Y@%H:%M:%S")),
            'description': ' '.join(settings.textBlob.split(' ')[0:size])
        })

    wiCollection.insert_many(documents=data)

    print('Creation finished: {}'.format(datetime.now()))

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    createTestData()
