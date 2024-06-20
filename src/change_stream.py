import pymongo
from datetime import datetime
import settings

def changeStream():
    client = pymongo.MongoClient(settings.uri)
    db = client.get_database(settings.dbName)

    if not settings.workItemHistoryCollection in db.list_collection_names():
        wiHistoryCollection = db.create_collection(settings.workItemHistoryCollection)
        wiHistoryCollection.create_index([{"_id": pymongo.DESCENDING}, "workItemID"], unique=True)
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
            "operationType": { "$in": ["insert", "update", "delete"] }
        }
    }])

    print("Change stream is listening on collection '{}' on server {} \n".format(settings.workItemCollection, db.client))

    for change in change_stream:
        headRevision = wiHistoryCollection.find_one({"_id": change["documentKey"]["_id"]})

        if headRevision is None:
            initialContent = wiCollection.find_one({"_id": change["documentKey"]["_id"]})

        currentRevision = revisionCollection.find_one({"revision": {"$gte": 0}})

        if change["operationType"] == "update":
            wiHistoryCollection.insert_one({"workItemID": change["documentKey"]["_id"],
                "change": change["updateDescription"]["updatedFields"],
                "modifiedBy": "Robby",
                "timeStamp": datetime.now(),
                "revision": currentRevision["revision"]
            })
            revisionCollection.update_one({"revision": {"$gte": 0}}, {"$inc": {"revision": 1}})

        if change["operationType"] == "insert": 
                if initialContent is not None: # keeping entire initial work item content
                    initialContent.pop("_id", None) # will get a new one anyway
                    initialContent["workItemID"] = change["documentKey"]["_id"]
                    initialContent["revision"] = currentRevision["revision"]
                    wiHistoryCollection.insert_one(initialContent)
                    revisionCollection.update_one({"revision": {"$gte": 0}}, {"$inc": {"revision": 1}})
        
        if change["operationType"] in ["delete"]:
            wiHistoryCollection.insert_one({"workItemID": change["documentKey"]["_id"],
                "change": "deleted",
                "modifiedBy": "Robby",
                "timeStamp": datetime.now(),
                "revision": currentRevision["revision"]
            })
            revisionCollection.update_one({"revision": {"$gte": 0}}, {"$inc": {"revision": 1}})

#------------------------ MAIN ------------------------#
if __name__ == "__main__":
    changeStream()
