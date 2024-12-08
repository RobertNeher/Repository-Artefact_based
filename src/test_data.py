import argparse
import json
import random
import sys
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import settings

WI_INDEX_NAME = "workItemIndex"

"""
u: Update
d: Delete
c: Create
r: Read (expects revisionID)
"""
def modifyTestData(wiCollection: Collection, workItemID:str, mode="u", revisionID=None):
    text = settings.textBlob.split(' ')
    a = random.randint(0, len(text))
    b = random.randint(0, len(text))

    if a > b:
        temp = a
        a = b
        b = temp

    wiCollection.update_many({'_id': ObjectId(workItemID)}, {'$set': {'description': ''.join(text[a:b]),
                                                        'modified': datetime.now()}})
#------------------------ CREATE -----------------------#
def create_workitem(wiCollection: Collection):
    dt = datetime.now()
    wordCount = len(settings.textBlob.split(' '))
    size = random.randint(0, wordCount)
    data = {
        'projectID': 1,
        'created': dt,
        'status': 'open',
        'createdBy': 'BHC',
        'title': f"Dataset {len(wiCollection.find().to_list())} as of {dt.strftime('%d. %b %Y@%H:%M:%S')}",
        'description': ' '.join(settings.textBlob.split(' ')[0:size])
    }
    wiCollection.insert_one(document=data)

    print('Creation finished: {}'.format(datetime.now()))
    print(data)

#------------------------ DETAILS ------------------------#
def workitem_details(wiCollection: Collection, workItemID: str):
    workItem = wiCollection.find_one(filter={'_id': ObjectId(workItemID)})
    print(workItem)

#---------------------- CONFIRMATION ----------------------#
def confirmation(workItemID: str) -> bool:
    """
    Ask user to confirm of work item.
    """
    answer = ""

    while answer not in ["y", "n"]:
        answer = input(f"Please confirm deletion of work item {workItemID} [y/N]? ").lower()
    return answer == "y"


###-------------------- MAIN ----------------------###
def main():
    # Create a new client and connect to the server
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client[settings.dbName]
    wiCollection = db.get_collection(settings.workItemCollection)

    parser = argparse.ArgumentParser(description='Modify data in repository',
                                     usage=f"{sys.argv[0]} [options]", allow_abbrev=False)
    parser.add_argument('-w', '--workItemID', nargs='?', help='work item ID (for modes==[d, r, u])')
    parser.add_argument('-m', '--mode', nargs='?', help='u: update, c: create, d: delete, r: print', default='r')

    args = parser.parse_args()

    if args.mode.strip() == "c":
        create_workitem(wiCollection=wiCollection)

    if args.workItemID is None and args.mode != "c":
        print("Please specify workItemID with modes (r)ead, (d)elete, or (u)pdate")
    else:

        if args.mode.strip() == "r":
            workitem_details(wiCollection=wiCollection, workItemID=args.workItemID.strip())
        if args.mode.strip() == "d":
            print(f"deleting work item {args.workItemID}")

            if confirmation(workItemID=args.workItemID):
                print("Yup")
            else:
                print("Nope")
        if args.mode.strip() == "u":
            modifyTestData(wiCollection=wiCollection, workItemID=args.workItem.strip(), )

if __name__ == "__main__":
    main()
