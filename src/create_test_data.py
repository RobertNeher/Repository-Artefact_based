import random

# from pymongo import DESCENDING
import settings
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def createTestData():
    # Create a new client and connect to the server
    projectID = 1
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client.get_database(settings.dbName)
    wiCollection = db.get_collection(settings.workItemCollection)

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
