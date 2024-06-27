from datetime import datetime
import src.settings as settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient(settings.uri, server_api=ServerApi('1'))
wiCollection = client[settings.dbName].get_collection(settings.workItemCollection)
data=[]
data.append({
    'projectID': 1,
    'created': datetime.now(),
    'status': 'open',
    'createdBy': 'BHC',
    'title': 'Dataset {} as of {}'.format("test", datetime.now().strftime("%d. %b %Y@%H:%M:%S")),
    'description': 'testtesttesttest'
})

wiCollection.insert_one(document=data[0])
