import sys
import argparse
# from datetime import datetime
# import src.settings as settings
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# client = MongoClient(settings.uri, server_api=ServerApi('1'))
# wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
# data=[]
# data.append({
#     'projectID': 1,
#     'created': datetime.now(),
#     'status': 'open',
#     'createdBy': 'BHC',
#     'title': 'Dataset {} as of {}'.format("test", datetime.now().strftime("%d. %b %Y@%H:%M:%S")),
#     'description': 'testtesttesttest'
# })

# wiCollection.insert_one(document=data[0])
def confirmation(workItemID: str) -> bool:
    """
    Ask user to confirm of work item.
    """
    answer = ""

    while answer not in ["y", "n"]:
        answer = input(f"Please confirm deletion of work item {workItemID} [y/N]? ").lower()
    return answer == "y"



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Modify data in repository',
                                     usage=f"{sys.argv[0]} [options]", allow_abbrev=False)
    parser.add_argument('-w', '--workItemID', nargs='?', help='work item ID (for modes==[d, r, u])')
    parser.add_argument('-m', '--mode', nargs='?', help='u: update, c: create, d: delete, r: print', default='r')

    args = parser.parse_args()
    # print(args.workItemID)
    # print(args.mode)

    if args.mode == "c":
        print("create a new work item with arbitrary content")

    if args.workItemID is None and args.mode != "c":
        print("Please specify workItemID with modes (r)ead, (d)elete, or (u)pdate")
    else:

        if args.mode == "r":
            print(f"details of work item {args.workItemID}")
        if args.mode == "d":
            print(f"deleting work item {args.workItemID}")

            if confirmation(workItemID=args.workItemID):
                print("Yup")
            else:
                    print("Nope")
        if args.mode == "u":
            print(f"updating work item {args.workItemID}")

