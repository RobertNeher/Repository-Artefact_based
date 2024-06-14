from datetime import datetime
import sys

import settings as settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def createBaseline(title: str, author: str):
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    baselineCollection = client[settings.dbName].get_collection(settings.baselineCollection)
    revision = client[settings.dbName].get_collection(settings.revisionsCollection)

    revisionID = revision.find_one({"revision": {"$gte": 0}})["revision"]

    # correct pre-emptive revision counter to point to latest transacion (AKA HEAD)
    revisionID -= 1

    try:
        baselineCollection.insert_one({"revision": revisionID,
                                         "title": title,
                                         "createdBy": author,
                                         "timeStamp": datetime.now()})
    finally:
        print("Baseline '{}' for revision '{}' created successfully.".format(title, revisionID))

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    # for createBaseline
    # if len(sys.argv) < 2:
    #     print("Please provide a baseline title.")
    #     sys.exit(0)

    # if len(sys.argv) == 3:
    #     createBaseline(title=sys.argv[2], author="Robby")

    # for compareBaselines
    if len(sys.argv) <= 2:
        print("Please specify workitem ID and at least one revision ID from which compare should start.\nIf there is no target revision, HED is assumed.")
        sys.exit(0)

    if len(sys.argv) == 3:
        compareBaselines(fromRevision=int(sys.argv[2]), toRevision=None)

    if len(sys.argv) == 4:
        compareBaselines(fromRevision=int(sys.argv[2]), toRevision=int(sys.argv[3]))
