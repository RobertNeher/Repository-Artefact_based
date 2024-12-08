import sys
import copy
import difflib
import settings

from datetime import datetime
from pathlib import Path
# from bson.json_util import dumps
from prepare_workitem import prepareWorkItem
from bson import ObjectId
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# def getDelta(workItemID: str, revisionFrom: str, revisionTo: str):
def getDelta(workItemID: str, fromRevisionID: int, **kwargs):
    workItemID = ObjectId(workItemID)
    revisionFrom = fromRevisionID

    # toRevisionID is optional, HEAD is default
    if kwargs.get('toRevisionID') is not None:
        revisionTo = kwargs.get('toRevisionID')
    else:
        revisionTo = None


    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
    wiHistoryCollection = client[settings.dbName].get_collection(settings.workItemHistoryCollection)

    baseWorkItem = wiCollection.find_one({"_id": workItemID})
    _baseWorkItem = copy.deepcopy(baseWorkItem)

    if revisionTo is not None:
        changes2Apply = wiHistoryCollection.find_one({"$and": [{"workItemID": workItemID}, {"revision": revisionTo}]})
        baseWorkItem = prepareWorkItem(_baseWorkItem, changes2Apply)
        _baseWorkItem = copy.deepcopy(baseWorkItem)

    changes2Apply = wiHistoryCollection.find_one({"$and": [{"workItemID": workItemID}, {"revision": revisionFrom}]})
    targetWorkItem = prepareWorkItem(_baseWorkItem, changes2Apply)

    compare1 = ',\n'.join(dumps(baseWorkItem).split(','))
    compare2 = ',\n'.join(dumps(targetWorkItem).split(','))

    html_diff = difflib.HtmlDiff(wrapcolumn=80).make_file(compare1.split('\n'), compare2.split('\n'),
                                                          fromdesc="Work item {} revision {}".format(workItemID, revisionFrom),
                                                          todesc="Work item {} revision {}".format(workItemID, revisionTo))
    Path('diff{}.html'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))).write_text(html_diff, encoding="utf-8")

    return html_diff

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Work item ID is missing")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Revision ID (from) is missing")
        sys.exit(0)

    elif len(sys.argv) == 4:
        getDelta(workItemID=sys.argv[1], fromRevisionID=int(sys.argv[2]), toRevisionID=int(sys.argv[3]))
    else:
        getDelta(workItemID=sys.argv[1], fromRevisionID=int(sys.argv[2]))
