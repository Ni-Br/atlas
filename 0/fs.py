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

def getDarks(pwd, imgName):
    hdu_list = pyfits.open(imgName)
    hdr = hdu_list[0].header
    expTime = hdr["EXPTIME"]
    dateObs = hdr["DATE-OBS"].split("T")
    darkList = []

    darkFile = open(pwd + ".darks")
    for dark in darkFile:
        darkName = dark.strip('\n')
        f = pyfits.open(darkName)
        darkHdr = f[0].header
        match = True
        if darkHdr["EXPTIME"] != expTime:
            match = False
        if dateObs[0] in darkHdr["DATE-OBS"]:
            match = False
        if match:
            log.v("Found dark, matches with  " + dark)
            darkList.append(dark)

    return darkList

def getBiass(pwd, imgName):
    return

def getFlats(pwd, imgName):
    return

def getUnprocessedImageNames(pwd):
    f = open(pwd + ".lights")
    filenames = []
    for line in f:
        fn = line.rstrip('\n')
        filenames.append(fn)
    return filenames
    #returnself.images.find({'AT_PROC': False, 'PICTTYPE': imgTypes()["Light"]})

def indexFiles(pwd):
    #os.remove(".flats")
    #os.remove(".biass")
    #os.remove(".darks")
    #os.remove(".lights")
    #os.remove(".errors")
    #os.remove(".unknowns")
    log.d("Looking for all *.fit* in " + pwd)
    fitsFiles = [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(pwd)
            for f in fnmatch.filter(files, "*.fit*")]
    #print(fitsFiles)
    for f in fitsFiles:
        log.d("Processing "+f)
        hdu_list = pyfits.open(f)
        hdu = hdu_list[0]
        hdr = hdu.header
        imgType = hdr["PICTTYPE"]
        outFile = "None"
        if isFlat(imgType):
            log.v(f + " is a flat.")
            outFile = ".flats"
        elif isDark(imgType):
            log.v(f + " is a dark")
            outFile = ".darks"
        elif isBias(imgType):
            log.v(f + " is a bias")
            outFile = ".biass"
        elif isLight(imgType):
            log.v(f + " is a light frame!")
            outFile = ".lights"
        elif isUnknown(imgType):
            log.w(f + " is of unknown type?")
            outFile = ".unknowns"
        else:
            log.wtf("ImgType not unknown or anything else??")
            outFile = ".errors"
        #TODO only open file once in w+ mode
        outputFile = open(pwd+outFile, 'a')
        outputFile.write(f + "\n")
    return
