import argparse
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
        print(f"Baseline '{title}' for revision '{revisionID}' created successfully.")

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Attach sample files to given work item',
                                     usage=f"{sys.argv[0]} [options]", allow_abbrev=False)
    parser.add_argument('-s', '--summary', nargs='?', help='Description of baselines (req\'d)')
    parser.add_argument('-a', '--author', nargs='?', help='User ID who creates the baseline.')

    args = parser.parse_args()

    if args.summary is None or args.author is None:
        parser.print_help()
        exit(-1)

    createBaseline(title=args.summary, author=args.author)