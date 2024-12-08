import hashlib
import os
import pickle
import sys

import bson
import settings as settings
from src.get_files import getFiles
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

BUF_SIZE = 8192

def computeHash(fileName: str):
    sha1 = hashlib.sha1()

    with open(fileName, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)

            if not data:
                break

            sha1.update(data)
    return sha1

def addAttachments(workItemID: str):
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    workItem = wiCollection.find_one({"_id": ObjectId(workItemID)})

    entries = []

    for file in getFiles(3):
        entry = {}

        with open(file, mode='rb') as attachmentBlob:
            print(file)
            entry['fileName'] = os.path.basename(file)
            entry['hash'] = bson.Binary(pickle.dumps(repr(computeHash(file))))
            entry['content'] = bson.Binary(pickle.dumps(repr(attachmentBlob)))
            entries.append(dict(entry))

    wiCollection.update_one({"_id": ObjectId(workItemID)}, {'$set': {'attachments': entries}})

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('A workitem ID is missing')
        sys.exit(1)

    addAttachments(sys.argv[1])
