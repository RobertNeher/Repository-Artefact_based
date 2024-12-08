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

def listChanges(workItemID:str, fromRevision:int, toRevision:int):
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client[settings.dbName]
    wiCollection = db.get_collection(settings.workItemCollection)
    wiHistoryCollection = db.get_collection(settings.workItemHistoryCollection)

    # get changes on work item
    if toRevision is None:
        changes = wiHistoryCollection.find({"$and": [{"workItemID": ObjectId(workItemID)}, {"revision": {"$gte": fromRevision}}]}).sort({"revision": DESCENDING})
    else:
        changes = wiHistoryCollection.find({"$and": [{"workItemID": ObjectId(workItemID)}, {"revision": {"$gte": fromRevision}}, {"revision": {"$lte": toRevision}}]}).sort({"revision": DESCENDING})

    baseWorkItem = loads(dumps(wiCollection.find_one({'_id': ObjectId(workItemID)})))
    diffs = HTMLHeader(title="Change log", docTitle="List of Changes")

    skipFirst = False
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
    if len(sys.argv) < 2:
        print('Work item ID is missing')
        sys.exit(0)

    if len(sys.argv) == 2:
        listChanges(workItemID=sys.argv[1], fromRevision=None)

    if len(sys.argv) == 3:
        listChanges(workItemID=sys.argv[1], fromRevision=int(sys.argv[2]), toRevision=None)

    if len(sys.argv) == 4:
        listChanges(workItemID=sys.argv[1], fromRevision=int(sys.argv[2]), toRevision=int(sys.argv[3]))
