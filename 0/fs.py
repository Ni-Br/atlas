import pyfits
import os
import fnmatch
import log

def isFlat(imgType):
    return imgType == 4
def isDark(imgType):
    return imgType == 3
def isBias(imgType):
    return imgType == 2
def isLight(imgType):
    return imgType == 1
def isUnknown(imgType):
    return imgType == 0

def imgTypes():
    return {"Unknown":0, "Light":1, "Bias":2, "Dark":3, "Flat":4}

def getDarks(imgName):
    return
    #date = self.getDateRange(imgName)
    #expTime = imgName['EXPTIME']
    #print(date)
    #print(expTime)
    #self.log.d("Finding darks from date:" + date + " and of exposure time:" + expTime)
    #res = self.images.find({'EXPTIME': expTime})
    #query = ({'DATE-OBS': {'$regex': '^'+date}, 'EXPTIME': expTime})
    #print(query)
    #return res

def getBiass(imgName):
    return

def getFlats(imgName):
    return

def getUnprocessedImageNames(pwd):
    return []
    #returnself.images.find({'AT_PROC': False, 'PICTTYPE': imgTypes()["Light"]})

def indexFiles(pwd):
    fitsFiles = [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(pwd)
            for f in fnmatch.filter(files, "*.fit*")]
    for f in fitsFiles:
        pass
        #TODO sort into fileType and create list files
    return
