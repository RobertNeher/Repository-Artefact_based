from datetime import datetime
import sys
import settings

from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def rollback(workItemID: str, revisionID: int, author: str):
    workItemID = ObjectId(workItemID)

    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    wiHistoryCollection = client[settings.dbName].get_collection(settings.workItemHistoryCollection)

    workItem = wiCollection.find_one({"_id": ObjectId(workItemID)})

    if "deleted" in workItem.keys() and workItem["deleted"]:
        workItem.pop("deleted", None)

        try:
            wiCollection.update_one({"_id": workItemID}, update={'$unset': {"deleted": None}})
        except:
            print("Rollback (recovery of workitem {}) did not work.".format(workItemID))
        finally:
            print("Rollback (recovery of workitem {}) succeeded.".format(workItemID))

    else:
        changes2Apply = wiHistoryCollection.find_one({"$and": [{"workItemID": workItemID}, {"revision": revisionID}]})

        if len(list(changes2Apply)) < 1:
            print("Revision {} is not valid for workitem '{}'".format(revisionID, workItemID))
            sys.exit(1)

        changes2Apply["change"]["modified"] = datetime.now()

        try:
            wiCollection.update_one({"_id": workItemID}, update={'$set': changes2Apply["change"]})
        except:
            print("Rollback of workitem {} to revision '{}' did not work.".format(workItemID, revisionID))
        finally:
            print("Rollback to content of revision '{}' succeeded.".format(revisionID))


#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Work item ID is missing")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Revision ID is missing")
        sys.exit(0)

    rollback(workItemID=sys.argv[1], revisionID=int(sys.argv[2]), author="Robby")
