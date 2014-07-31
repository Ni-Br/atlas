import os
import pyfits
import logging
import fnmatch

def getHeader(filename):
    logger = logging.getLogger(__name__)
    f = pyfits.open(filename)
    return f[0].header

def writeListToFile(filename, array):
    logger = logging.getLogger(__name__)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, 'w+')
    for element in array:
        f.write(str(element) + '\n')

def readFileToArray(filename):
    logger = logging.getLogger(__name__)
    if not os.path.isfile(filename):
        return []
    f = open(filename, 'r')
    array = []
    for line in f:
        text = line.strip('\n')
        array.append(text)
    return array
