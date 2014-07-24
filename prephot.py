import os
#import log
import fnmatch
import fs
import pyfits

#get all .corr
root = os.getcwd()+"/"
corrFnList = [os.path.relpath(os.path.join(dirpath, f), root)
                    for dirpath, dirnames, files in os.walk(root)
                                for f in fnmatch.filter(files, "*.corr")]

def genCooFile(ooi, starList, fn):
    #We want field_x&y for center
    #We want index_ra&dec for coords
    #Would be interesting to see if flux&background give enough to lightcurve...
    coords = []
    coords.append(str(int(ooi["field_x"])) + " " + str(int(ooi["field_y"])))
    for line in starList:
        if int(ooi["field_x"]) != int(line.field("field_x")) or int(ooi["field_y"]) != int(line.field("field_y")):
            coords.append(str(int(line.field("field_x"))) + " " + str(int(line.field("field_y"))))

    fs.writeListToFile(fn, coords)
    return coords

def genImexamInsts(star, fn):
    #figure out which is target star
    insts = [':s ' + str(int(star["field_x"])) + ' ' + str(int(star["field_y"]))]

    fs.writeListToFile(fn, insts)
    return insts

def genImexamInstsAlt(starList, fn):
    #figure out which is target star
    insts = []
    for star in starList:
        insts.append(':s ' + str(star.field('field_x')) + ' ' + str(star.field('field_y')))

    fs.writeListToFile(fn, insts)
    return insts

def getExoplanetList():
    exoplanetListFn = "/home/astron/bin/atlas/exoplanetList"
    return [i.split(",") for i in fs.readFileToArray(exoplanetListFn)]

def areEqual(a, b, precision = 3):
    return abs(a-b) <= pow(10, -precision)

exoStarList = getExoplanetList()
for corrFn in corrFnList:
    print("opening " + corrFn)
    f = pyfits.open(corrFn)
    bfn = os.path.splitext(corrFn)[0]
    starList = f[1].data
    ooi = {}
    starNotFound = True
    for star in starList:
        for exoStar in exoStarList:
            if areEqual(float(star.field("index_ra")),float(exoStar[0])) and areEqual(float(star.field("index_dec")), float(exoStar[1])):
                starNotFound = False
                ooi["index_ra"] = star.field("index_ra")
                ooi["index_dec"] = star.field("index_dec")
                ooi["field_x"] = star.field("field_x")
                ooi["field_y"] = star.field("field_y")
                break;

    if starNotFound:
        print("404 - STAR NOT FOUND: " + bfn)
        continue
    genImexamInsts(ooi, root + bfn + ".imInst")
    genCooFile(ooi, starList, root + bfn + ".coo")
