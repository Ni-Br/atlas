import pyfits
import argparse
import fs
import os
import logging
import fnmatch

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

def getDarks(root, imgName):
    logger = logging.getLogger(__name__)
    #hdu_list = pyfits.open(root + imgName)
    #hdr = hdu_list[0].header
    hdr = fs.getHeader(root + imgName)
    #expTime = hdr["EXPTIME"]
    dateObs = hdr["DATE-OBS"].split("T")
    darkList = []

    logger.debug("Looking for darks from date: " + dateObs[0]) 
    darks = fs.readFileToArray(root + ".darks")
    darkList = []
    for dark in darks:
        darkHdr = fs.getHeader(root + dark)
        match = True
        #if darkHdr["EXPTIME"] != expTime:
            #match = False
        if dateObs[0] not in darkHdr["DATE-OBS"]:
            match = False
        if match:
            #logger.debug("Found dark, matches with  " + dark)
            darkList.append(dark)

    return darkList

def getBiass(root, imgName):
    logger = logging.getLogger(__name__)
    hdr = fs.getHeader(root + imgName)
    dateObs = hdr["DATE-OBS"].split("T")
    biasList = []

    logger.debug("Looking for biass from date: " + dateObs[0])
    biass = fs.readFileToArray(root + ".biass")
    biassList = []
    for bias in biass:
        biasHdr = fs.getHeader(root + bias)
        match = True
        if dateObs[0] not in biasHdr["DATE-OBS"]:
            match = False
        if match:
            #logger.debug("Found bias, matches with  " + bias)
            biasList.append(bias)
    return biasList

def getFlats(root, imgName):
    logger = logging.getLogger(__name__)
    hdr = fs.getHeader(root + imgName)
    dateObs = hdr["DATE-OBS"].split("T")
    flatList = []

    logger.debug("Looking for flats from date: " + dateObs[0])
    flats = fs.readFileToArray(root + ".flats")
    flatsList = []
    for flat in flats:
        flatHdr = fs.getHeader(root + flat)
        match = True
        if dateObs[0] not in flatHdr["DATE-OBS"]:
            match = False
        if match:
            #logger.debug("Found flat, matches with  " + flat)
            flatsList.append(flat)
    return flatsList

def getUnprocessedImageNames(root):
    logger = logging.getLogger(__name__)
    fileContents = fs.readFileToArray(root + ".lights")
    fileContents = [f.split(":")[0] for f in fileContents]
    filenames = []
    proc = fs.readFileToArray(root + ".proc")
    
    for fn in fileContents:
        if fn not in proc:
            filenames.append(fn)
    filenames.sort()
    return [f.split(":")[0] for f in filenames]

def getUnprocessedFlatFn(root):
    logger = logging.getLogger(__name__)
    fileContents = fs.readFileToArray(root + ".flats")
    filenames = []
    proc = fs.readFileToArray(root + ".proc")
    
    for fn in fileContents:
        if fn not in proc:
            filenames.append(fn)
    filenames.sort()
    return filenames

def indexFiles(root):
    logger = logging.getLogger(__name__)
    logger.debug("Looking for all *.fit* in " + root)
    fitsFiles = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, "*.fit")]
    fitsFiles.sort()
    #print(fitsFiles)
 
    listDarks = fs.readFileToArray(root + ".darks")
    listBiass = fs.readFileToArray(root + ".biass")
    listFlats = fs.readFileToArray(root + ".flats")
    listLights = fs.readFileToArray(root + ".lights")
    listUnknowns = fs.readFileToArray(root + ".unknowns")
    listErrors = fs.readFileToArray(root + ".errors")
    index = fs.readFileToArray(root + ".index")

    for f in fitsFiles:
        if f in index:
            continue
        if "atlas_" in f:
            continue
        logger.debug("Indexing "+f)
        hdr = fs.getHeader(root + f)
        imgType = hdr["PICTTYPE"]
        outFile = "None"
        date = hdr["DATE-OBS"].split("T")[0]
        if isFlat(imgType):
            #logger.debug(f + " is a flat.")
            listFlats.append(f)
        elif isDark(imgType):
            #logger.debug(f + " is a dark")
            listDarks.append(f)
        elif isBias(imgType):
            #logger.debug(f + " is a bias")
            listBiass.append(f)
        elif isLight(imgType):
            #logger.debug(f + " is a light frame!")
            listLights.append(f + ":" + date)
        elif isUnknown(imgType):
            logger.warning(f + " is of unknown type?")
            listUnknowns.append(f)
        else:
            logger.error("ImgType not unknown or anything else??")
            listErrors.append(f)
        #TODO only open file once in w+ mode
        index.append(f)
    fs.writeListToFile(root+".flats", listFlats)
    fs.writeListToFile(root+".darks", listDarks)
    fs.writeListToFile(root+".biass", listBiass)
    fs.writeListToFile(root+".lights", listLights)
    fs.writeListToFile(root+".unknowns", listUnknowns)
    fs.writeListToFile(root+".errors", listErrors)
    fs.writeListToFile(root+".index", index)
    return

if __name__ == "__main__":
    ##Parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("root", default=".", help="Search for images in specified directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Outputs contents of log to stdout as well as to the log file")
    parser.add_argument("-o", "--output", default="atlas_1/", help="Output directory")

    args = parser.parse_args()

    root = args.root
    logLevel = args.verbose
    outputDir = args.output

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("Indexing " + root)
    indexFiles(root)

    logger.info("Getting unprocessed images")
    unprocImgNames = getUnprocessedImageNames(root)
    if not unprocImgNames or len(unprocImgNames) == 0:
        logger.info("No unprocessed images.")
        #TODO stop the program?
    unprocImgNames.sort()

    logger.info("Processing " + str(len(unprocImgNames)) + " images")
    biassFiles = {}
    darksFiles = {}
    flatsFiles = {}
    procFiles = fs.readFileToArray(root + ".proc")

    for img in unprocImgNames:
        logger.debug("Getting calibration images for " + img)
        hdr = fs.getHeader(root + img)
        exptime = hdr['EXPTIME']
        date = hdr['DATE-OBS'].split('T')
        date = date[0]
        datexp = date + ":" + str(exptime)
        #Darks
        if date in darksFiles:
            darksFiles[date].append(img)
        else:
            darks = getDarks(root, img)
            darksFiles[date] = [img]
            if len(darks) > 0:
                fs.writeListToFile(root + outputDir + ".debugarks:" + date, darks)
        #Biass
        if date in biassFiles:
            biassFiles[date].append(img)
        else:
            biass = getBiass(root, img)
            biassFiles[date] = [img]
            if len(biass) > 0:
                fs.writeListToFile(root + outputDir + ".biass:" + date, biass)
        #Flats
        if date in flatsFiles:
            flatsFiles[date].append(img)
        else:
            flats = getFlats(root, img)
            flatsFiles[date] = [img]
            if len(flats) > 0:
                fs.writeListToFile(root +outputDir + ".flats:" + date, flats)
        #TODO deal with not good darks
        #TODO deal with lack of flats
        #TODO deal with weird timing for calibration (before vs. after)
        procFiles.append(img)

    listFlats = getUnprocessedFlatFn(root)
    logger.info("Getting darks for " + str(len(listFlats)) + " flats")
    for flat in listFlats:
        logger.debug("Getting calbration images for " + flat)
        hdr = fs.getHeader(root + flat)
        date = hdr['DATE-OBS'].split('T')
        date = date[0]
        if date in darksFiles:
            darksFiles[date].append(flat)
        else:
            darks = getDarks(root, flat)
            darksFiles[date] = [flat]
            if len(darks) > 0:
                fs.writeListToFile(root + outputDir + ".darks:" + date, darks)
        procFiles.append(flat)

    fs.writeListToFile(root + ".proc", procFiles)
