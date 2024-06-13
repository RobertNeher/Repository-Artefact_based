from datetime import datetime
import difflib
from pathlib import Path
from bson.json_util import dumps, loads
import sys
from prepare_workitem import prepareWorkItem
import settings as settings
# from datetime import datetime
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING

HTML_HEADER = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>

<head>
    <meta http-equiv="Content-Type"
          content="text/html; charset=utf-8" />
    <title></title>
    <style type="text/css">
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}
    </style>
</head>

<body>
"""

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
    diffs = HTML_HEADER

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
        listChanges(workItemID=sys.argv[1])

    if len(sys.argv) == 3:
        listChanges(workItemID=sys.argv[1], fromRevision=int(sys.argv[2]), toRevision=None)

    if len(sys.argv) == 4:
        listChanges(workItemID=sys.argv[1], fromRevision=int(sys.argv[2]), toRevision=int(sys.argv[3]))
