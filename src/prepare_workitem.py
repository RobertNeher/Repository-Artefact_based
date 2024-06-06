import copy

def prepareWorkItem(workItem, changes2Apply):
    value = copy.deepcopy(workItem)

    for key in changes2Apply["change"].keys():
        value[key] = changes2Apply["change"][key]

    return value
