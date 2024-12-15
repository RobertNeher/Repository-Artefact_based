import copy

def prepareWorkItem(workItem, changes2Apply):
    value = copy.deepcopy(workItem)

    if "change" in changes2Apply.keys():
        for key in changes2Apply["change"].keys():
            value[key] = changes2Apply["change"][key]

        return value
    else: # why does this happen?
        return None
