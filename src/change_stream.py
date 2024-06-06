import pymongo
from datetime import datetime
import settings

def changeStream():
    client = pymongo.MongoClient(settings.uri)
    db = client.get_database(settings.dbName)

    if not settings.workItemHistoryCollection in db.list_collection_names():
        wiHistoryCollection = db.create_collection(settings.workItemHistoryCollection)
        wiHistoryCollection.create_index([{"_id",pymongo.DESCENDING}, "wiID"], unique=True)
    else:
        wiHistoryCollection = db[settings.workItemHistoryCollection]

    if not settings.revisionsCollection in db.list_collection_names():
        revisionCollection = db.create_collection(settings.revisionsCollection)
        revisionCollection.insert_one({"revision": 0})
    else:
        revisionCollection = db[settings.revisionsCollection]

    wiCollection = db.get_collection(settings.workItemCollection)

    change_stream = wiCollection.watch([{
        "$match": {
            "operationType": { "$in": ["insert", "update"] }
        }
    }])

    print("Change stream is listening on collection '{}' on server {} \n".format(settings.workItemCollection, db.client))

    for change in change_stream:
        if change["operationType"] in ["update", "insert"]:
            currentRevision = revisionCollection.find_one({"revision": {"$gte": 0}})
            wiHistoryCollection.insert_one({"wiID": change["documentKey"]["_id"],
                "change": change["updateDescription"]["updatedFields"],
                "editor": "Robby",
                "timeStamp": datetime.now(),
                "revision": currentRevision["revision"]
            })
            revisionCollection.update_one({"revision": {"$gte": 0}}, {"$inc": {"revision": 1}})

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    changeStream()
