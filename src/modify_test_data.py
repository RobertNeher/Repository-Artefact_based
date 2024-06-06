import random
import sys
from datetime import datetime
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import settings

WI_INDEX_NAME = "workItemIndex"

def modifyTestData(workItemID:str):
    # Create a new client and connect to the server
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client[settings.dbName]
    wiCollection = db.get_collection(settings.workItemCollection)

    text = settings.textBlob.split(' ')
    a = random.randint(0, len(text))
    b = random.randint(0, len(text))

    if a > b:
        temp = a
        a = b
        b = temp

    wiCollection.update_many({'_id': ObjectId(workItemID)}, {'$set': {'description': ''.join(text[a:b]),
                                                    'modified': datetime.now()}})

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) == 2:
        modifyTestData(sys.argv[1])
    else:
        print("Please specify a work item ID")
        sys.exit(1)
