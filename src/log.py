from datetime import datetime
from pathlib import Path
import sys
import settings as settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING
from bson import ObjectId
from html_header import HTMLHeader

def getLog(workItemID: str):
    client = MongoClient(settings.uri, server_api=ServerApi('1'))
    db = client[settings.dbName]
    wiCollection = db.get_collection(settings.workItemCollection)
    wiHistoryCollection = db.get_collection(settings.workItemHistoryCollection)
    logOutput = ""

    if workItemID != None:
        workItem = wiCollection.find_one({"_id": ObjectId(workItemID)})
        changes = wiHistoryCollection.find({"workItemID": ObjectId(workItemID)}).sort({"revision": DESCENDING})
        logOutput += HTMLHeader(title=f"Log for work item {workItemID}", docTitle=f"Changes for work item {workItemID}")
    else:
        changes = wiHistoryCollection.find({}).sort({"revision": DESCENDING})
        logOutput += HTMLHeader(title=f"Complete Log", docTitle="All changes in repository")

    logOutput += f"""
<br/>
<body>
    <table width: 70%>
    <colgroup>
       <col span="1" style="width: 10%;">
       <col span="1" style="width: 10%;">
       <col span="1" style="width: 10%;">
       <col span="1" style="width: 30%;">
    </colgroup>
    <tr>
        <th>Revision</th>
        <th>Editor</th>
        <th>Timestamp</th>
        <th>Changes</th>
    </tr>"""

    for change in changes:
        logOutput += f"""
    <tr>
        <td align="center">{change["revision"]}</td>"""
        
        if "modifiedBy" in change.keys():
            logOutput += f"""
        <td align="center">{change["modifiedBy"]}</td>"""
        else: # for historic reason
            logOutput += f"""
        <td align="center">{change["editor"]}</td>"""

        logOutput += f"""
            <td align="center">{change["timeStamp"].strftime("%Y%m%d-%H:%M:%S")}</td>"""

        if "change" in change.keys():
            if len(change["change"]) == 0:
                logOutput += f"""
            <td>Recovery from deletion</td>"""
            else:
                logOutput += f"""
    <td>
    <table>
        <tr>
            <th>Field</th>
            <th>Content</th>
        </tr>
        <tr>
    """
                for key in change["change"].keys():
                    logOutput += f"""
                <tr>
                    <td>{key}</td>"""
                    if isinstance(change["change"][key], datetime):
                        logOutput += f"""
                    <td>{(change["change"][key]).strftime("%d. %B %Y@%H:%M:%S")}</td>"""
                    if isinstance(change["change"][key], str):
                        logOutput += f"""
                    <td>{change["change"][key][:20]}</td>"""
                    if isinstance(change["change"][key], bool):
                        logOutput += f"""
                    <td>Item has been deleted</td>
                </tr>"""

                logOutput += """
            </table>
        </td>"""

    logOutput += """
    </table>
    </body>

    </html>
    """
    Path('log{}.html'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))).write_text(logOutput)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        getLog(sys.argv[1])
    else:
        getLog(None)
