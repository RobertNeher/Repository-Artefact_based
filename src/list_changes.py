import argparse
from datetime import datetime
import difflib
from pathlib import Path
from bson.json_util import dumps, loads
import sys
from prepare_workitem import prepareWorkItem
import settings as settings
from html_header import HTMLHeader
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING

def listChanges(database:MongoClient, workItemID:str, fromRevision:int=0, toRevision:int=0):
    # client = MongoClient(settings.uri, server_api=ServerApi('1'))
    # db = client[settings.dbName]
    wiCollection = database.get_collection(settings.workItemCollection) # type: ignore
    wiHistoryCollection = database.get_collection(settings.workItemHistoryCollection) # type: ignore

    # get changes on work item
    if toRevision == 0:
        changes = wiHistoryCollection.find({"$and": [{"workItemID": ObjectId(workItemID)}, {"revision": {"$gte": fromRevision}}]}).sort({"revision": DESCENDING})
    else:
        changes = wiHistoryCollection.find({"$and": [{"workItemID": ObjectId(workItemID)}, {"revision": {"$gte": fromRevision}}, {"revision": {"$lte": toRevision}}]}).sort({"revision": DESCENDING})

    baseWorkItem = loads(dumps(wiCollection.find_one({'_id': ObjectId(workItemID)})))
    diffs = HTMLHeader(title="Change log", docTitle="List of Changes")

    skipFirst = toRevision is None

    for change in changes:
        # first entry is the head revision
        if skipFirst:
            skipFirst = False
            continue

        deltas = loads(dumps(change))
        targetWorkItem = prepareWorkItem(baseWorkItem, deltas)
        compare1 = ',\n'.join(dumps(baseWorkItem).split(','))
        compare2 = ',\n'.join(dumps(targetWorkItem).split(','))

        html_diff = difflib.HtmlDiff(wrapcolumn=80).make_table(compare1.split('\n'),
                                                               compare2.split('\n'),
                                                               fromdesc="base item " + str(baseWorkItem['_id']) + " with rev. " + str(change["revision"]),
                                                               todesc="rev. " + str(change["revision"]),
                                                            #    context=False
                                                              )
        diffs += html_diff

    diffs += """
</body>

</html>
"""
    Path('diff{}.html'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))).write_text(diffs)


#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    #get latest revision
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client[settings.dbName]
    revisions = db.get_collection(settings.revisionsCollection)
    latestRevision = revisions.find_one({})["revision"] - 1 # type: ignore

    parser = argparse.ArgumentParser(description='Attach sample files to given work item',
                                     usage=f"{sys.argv[0]} [options]")
    parser.add_argument('-w', '--workItemID', nargs='?', help='work item ID (req\'d)')
    parser.add_argument('-f', '--fromRevision', nargs='?', help='Starting revision')
    parser.add_argument('-t', '--toRevision', nargs='?', help='Ending revision', const='')

    args = parser.parse_args(   )

    if args.workItemID is None:
        parser.print_usage()
        exit(-1)

    fromRevision = 0
    toRevision = latestRevision

    if args.toRevision is None:
        toRevision = latestRevision
    else:
        toRevision = int(args.toRevision.strip())

    if args.fromRevision is not None:
        fromRevision = int(args.fromRevision.strip())

        listChanges(database=db, workItemID=args.workItemID.strip(), fromRevision=fromRevision, toRevision=toRevision) # type: ignore
