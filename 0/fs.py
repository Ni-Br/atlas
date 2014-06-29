import pymongo
import pyfits
import log

class Run:
    def __init__(s, args):
        #TODO extract everything from database

        return
         
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

class FS:
    def __init__(self, pwd, log):
        self.client = pymongo.MongoClient()
        self.log = log
        self.db = self.client.atlas_given
        self.name = pwd
        self.images = self.db.images
        return

    def getDateRange(self, header):
        date = header['DATE-OBS']
        date = date.split('T')
        self.log.v("Date of " + header['_id'] + " is " + date[0])
        return date[0]

    def getImg(self, img):
        self.images.find({'_id':img})
        return

    def getDarks(self, header):
        date = self.getDateRange(header)
        expTime = header['EXPTIME']
        print date
        print expTime
        #self.log.d("Finding darks from date:" + date + " and of exposure time:" + expTime)
        res = self.images.find({'EXPTIME': expTime})
        query = ({'DATE-OBS': {'$regex': '^'+date}, 'EXPTIME': expTime})
        print query
        return res

    def getBiass(self, header):
        return

    def getFlats(self, header):
        return

    def getUnprocessedImages(self):
        return self.images.find({'AT_PROC': False, 'PICTTYPE': imgTypes()["Light"]})

    def addData(self, img):
        self.log.v("Adding "+ img)
        self.log.v(img)
        fitsHeader = pyfits.getheader(img)
        dictHeader = {'_id': img}
        dictHeader = {'AT_ENV': self.name}
        dictHeader['AT_PROC'] = False
        for key in fitsHeader:
            if key in dictHeader:
                dictHeader[key] += "/" + fitsHeader[key] #Does this always work?
            else:
                dictHeader[key] = fitsHeader[key]
        self.images.update({"_id":img}, dictHeader, upsert=True)
        self.log.v(dictHeader)

    def addEvent(self, event):
        return

def addList(imgList, fs):
    for img in imgList:
        fs.addData(img)
