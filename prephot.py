import os
import subprocess
import sys
import logging
import fnmatch
import fs
import pyfits

def getxyFromRaDec(fn, ra, dec):
    logger = logging.getLogger(__name__)
    try:
        output = subprocess.check_output(["wcs-rd2xy", "-w", fn + ".wcs", "-r", str(ra), "-d", str(dec)])
    except subprocess.CalledProcessError as e:
        logger.error("wcs-rd2xy:" + str(e.output))
    output = str(output)

    #ouput format is RA,Dec (val, val) -> pixel (val, val)
    output = output.split(">")[1]
    output = output.split("(")[1]
    x = output.split(",")[0]
    y = output.split(" ")[1]
    y = y.split(")")[0]
    return x, y

def genCooFile(ooi, starList, fn):
    #We want x&y for center
    #We want index_ra&dec for coords
    #Would be interesting to see if flux&background give enough to lightcurve...
    coords = []
    coords.append(str(int(ooi["x"])) + " " + str(int(ooi["y"])))
    for line in starList:
        if int(ooi["x"]) != int(line.field("x")) or int(ooi["y"]) != int(line.field("y")):
            coords.append(str(int(line.field("x"))) + " " + str(int(line.field("y"))))

    fs.writeListToFile(fn, coords)
    return coords

def genImexamInsts(star, fn):
    #figure out which is target star
    insts = [':s ' + str(int(star["x"])) + ' ' + str(int(star["y"]))]

    fs.writeListToFile(fn, insts)
    return insts

def genImexamInstsAlt(starList, fn):
    #figure out which is target star
    insts = []
    for star in starList:
        insts.append(':s ' + str(star.field('x')) + ' ' + str(star.field('y')))

    fs.writeListToFile(fn, insts)
    return insts

def getExoplanetList():
    exoplanetListFn = "/home/astron/bin/atlas/exoplanetList"
    exoList = [i.split(",") for i in fs.readFileToArray(exoplanetListFn)]
    exoDic = []
    for line in exoList:
        dic = {}
        dic["name"] = line[0]
        dic["ra"] = line[1]
        dic["dec"] = line[2]
        exoDic.append(dic)
    return exoDic

def areEqual(a, b, precision = 10**(-3)):
    return abs(float(a)-float(b)) <= precision

def isInField(fn, ra, dec):
    wcsList = [i.split(" ") for i in fs.readFileToArray(fn + ".wcs.center")]
    wcsDict = {}
    for key, value in wcsList:
        wcsDict[key] = value

    return areEqual(ra, wcsDict["ra_center"], 0.166) and areEqual(dec, wcsDict["dec_center"], 0.166)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    exoStarList = getExoplanetList()
    runs = {}
    runBfns = {}
    runOOI = {}
    #get all .corr
    root = sys.argv[1]
    baseFnList = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root))[0]
                        for dirpath, dirnames, files in os.walk(root)
                                    for f in fnmatch.filter(files, "*.solved")]
    baseFnList.sort()

    for bfn in baseFnList:
        logger.debug("opening " + bfn)
        hdr = fs.getHeader(root + bfn + ".fits")
        date = hdr["DATE-OBS"].split("T")[0]

        #Find out what we're looking at
        ooi = {}
        starNotFound = True
        for exostar in exoStarList:
            if isInField(root + bfn, exostar["ra"], exostar["dec"]):
                starNotFound = False
                ooi = exostar
                logger.debug("the star is: " + ooi["name"])

        if starNotFound:
            logger.info("404 - STAR NOT FOUND: " + bfn)
            continue

        #Figure out what sources are visible for all fields
        f = pyfits.open(root + bfn + ".rdls")
        rdSources = f[1].data

        index = date + ooi["name"] 
        #TODO use sets
        #TODO use columns instead of 0 and 1
        if index in runs:
            runBfns[index].append(bfn)
            new = []

            for source in runs[index]:
                if isInField(root + bfn, source["RA"], source["DEC"]):
                    new.append(source)

            runs[index] = new
        else:
            runs[index] = rdSources
            runBfns[index] = [bfn]

            runOOI[index] = ooi

    #Output to files
    for index in runs:
        fs.writeListToFile(root + "atlas_" + index + ".atlas.rdls", runs[index])
        ooi = runOOI[index]
        for bfn in runBfns[index]:
            x, y = getxyFromRaDec(root + bfn, ooi["ra"], ooi["dec"])
            coords = [str(x) + " " + str(y)]

            for ra, dec in runs[index]:
                if not areEqual(ra, ooi["ra"]) or not areEqual(dec, ooi['dec']):
                    x, y = getxyFromRaDec(root + bfn, ra, dec)
                    coords.append(str(x) + " " + str(y))
            fs.writeListToFile(root + bfn + ".coo", coords)

        magFileArray = [root + fn + ".mag" for fn in runBfns[index]]
        fs.writeListToFile(root + "atlas_" + index + ".txdmp", magFileArray)
