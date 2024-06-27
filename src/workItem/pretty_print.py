def prettyPrint(workItem: dict) -> None:
    output = f"""
Project ID: {workItem["projectID"]}
ID: {workItem["_id"]}"""
    if "revision" in workItem.keys():
        output += f"""\nRevision: {workItem["revision"]}\n"""

    output += f"""Title: {workItem["title"]}
Status: {workItem["status"]}
Created by: {workItem["createdBy"]}"""
# Last modification: {workItem["modified"]}"""
    if "modified" in workItem.keys():
        output += f"""\nLast modification: {workItem["modified"]}"""

    output += f"""\nDescription:\n{workItem["description"]}"""
    print(output)