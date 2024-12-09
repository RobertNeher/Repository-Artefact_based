import argparse
from datetime import datetime
import sys
import settings

from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def deleteWorkItem(workItemID: str) -> bool:
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    wiCollection.update_one({"_id": ObjectId(workItemID)}, update={'$set': {"deleted": True}})

    return True

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete work item',
                                     usage=f"{sys.argv[0]} [options]", allow_abbrev=False)
    parser.add_argument('-w', '--workItemID', nargs='?', help='work item ID (req\'d)')

    args = parser.parse_args()

    if args.workItemID is None:
        parser.print_usage()
        exit(-1)

    deleteWorkItem(workItemID=args.workItemID)
    print(f"Work item {args.workItemID} marked as deleted")
