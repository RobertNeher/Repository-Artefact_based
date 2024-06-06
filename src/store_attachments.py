from pathlib import Path
import pickle
import sys

from prepare_workitem import prepareWorkItem
import settings as settings
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def storeAttachments(workItemID: str, revision: int):
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    workItem = wiCollection.find_one({"_id": ObjectId(workItemID)})

    if revision is not None:
        wiHistoryCollection = client[settings.dbName].get_collection(settings.workItemHistoryCollection)
        changes2Apply = wiHistoryCollection.find_one({"$and": [{"wiID": ObjectId(workItemID)}, {"revision": revision}]})
        workItem = prepareWorkItem(workItem, changes2Apply)

    if not "attachments" in workItem.keys():
        return None

    for blob in workItem["attachments"]:
        fileName = blob["fileName"]
        hash = blob["hash"]
        content = pickle.loads(blob["content"])
        Path(fileName).write_text(content)
              
#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('A workitem ID is missing')
        exit(1)
    if len(sys.argv) == 2:
        storeAttachments(sys.argv[1], revision=None)
    else:
        storeAttachments(sys.argv[1], revision=int(sys.argv[2]))
