import random
import os
import settings as settings
from os import listdir
from os.path import isfile, join


def getFiles(maxFiles = 3):
    fileList = []
    for file in [file for file in listdir(os.path.abspath(settings.UPLOAD_FOLDER))]:
        if isfile(join(os.path.abspath(settings.UPLOAD_FOLDER), file)):
            fileList.append(join(os.path.abspath(settings.UPLOAD_FOLDER), file))

    _fileList = []

    for i in range(random.randint(0, maxFiles)):
        _fileList.append(fileList[random.randint(0, len(fileList)-1)])

    return _fileList
