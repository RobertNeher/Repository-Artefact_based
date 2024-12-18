import argparse
import hashlib
import os
import pickle
import sys

import bson
import settings as settings
from get_files import getFiles
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
    parser = argparse.ArgumentParser(description='Attach sample files to given work item',
                                     usage=f"{sys.argv[0]} [options]", allow_abbrev=False)
    parser.add_argument('-w', '--workItemID', nargs='?', help='work item ID (req\'d)')

    args = parser.parse_args()

    if args.workItemID is None:
        parser.print_usage()
        exit(-1)

    addAttachments(args.workItemID)
