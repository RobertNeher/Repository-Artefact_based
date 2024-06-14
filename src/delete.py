from datetime import datetime
import sys
import settings

from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def deleteWorkItem(workItemID: str) -> bool:
    workItemID = ObjectId(workItemID)

    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    wiCollection.update_one({"_id": workItemID}, update={'$set': {"deleted": True, "status": "Obsolete"}})
                               
                               
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Work item ID is missing")
        sys.exit(0)

    deleteWorkItem(workItemID=sys.argv[1])
