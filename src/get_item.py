from copy import deepcopy
from datetime import datetime
import sys
from prepare_workitem import prepareWorkItem
from pretty_print import prettyPrint
import settings

from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING, DESCENDING


def getWorkItemRevision(wiID: str, revisionID: int):
    workItemID = ObjectId(wiID)

    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiHistoryCollection = client[settings.dbName].get_collection(settings.workItemHistoryCollection)

    workItemInitialState = wiHistoryCollection.find({"workItemID": workItemID}).sort({"revision": ASCENDING})[0]
    if revisionID is None:
        changes = wiHistoryCollection.find({"workItemID": workItemID}).sort({"revision": ASCENDING})
    else:
        changes = wiHistoryCollection.find({"$and": [{"workItemID": workItemID}, {"revision": {"$lte": revisionID}}]}).sort({"revision": ASCENDING})

    if len(list(changes)) < 1:
        print("No changes for workitem '{}' so far.".format(workItemID))
        sys.exit(1)

    workItem = deepcopy(workItemInitialState)

    for change in changes:

        if "change" in change.keys():
            if len(change["change"]) == 0 and change["revision"] == revisionID:
                print(f"Work item '{change["workItemID"]} is being flagged as deleted at revision {change["revision"]}")
                break

        workItem = prepareWorkItem(change["workItemID"], change["change"])  
    
    if revisionID is not None:
        workItem["revision"] = revisionID

    prettyPrint(workItem)

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Work item ID is missing")
        sys.exit(0)

    if len(sys.argv) == 3:
        getWorkItemRevision(wiID=sys.argv[1], revisionID=int(sys.argv[2]))
    else:
        getWorkItemRevision(wiID=sys.argv[1], revisionID=None)
