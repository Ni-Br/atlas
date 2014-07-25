import os
#import log
import fnmatch
import fs
import pyfits

#get all .corr
root = os.getcwd()+"/"
baseFnList = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root))[0]
                    for dirpath, dirnames, files in os.walk(root)
                                for f in fnmatch.filter(files, "*.solved")]
baseFnList.sort()

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

def areEqual(a, b, precision = 3):
    return abs(a-b) <= pow(10, -precision)

exoStarList = getExoplanetList()
for bfn in baseFnList:
    print("opening " + bfn)
    f = pyfits.open(bfn + ".new")
    starList = f[1].data
    ooi = {}
    starNotFound = True
    for star in starList:
        for exoStar in exoStarList:
            if areEqual(float(star.field("index_ra")),float(exoStar["ra"])) and areEqual(float(star.field("index_dec")), float(exoStar["dec"])):
                starNotFound = False
                ooi["index_ra"] = star.field("index_ra")
                ooi["index_dec"] = star.field("index_dec")
                ooi["x"] = star.field("field_x")
                ooi["y"] = star.field("field_y")
                break;

    if starNotFound:
        print("404 - STAR NOT FOUND: " + bfn)
        continue
    genImexamInsts(ooi, root + bfn + ".imInst")
    genCooFile(ooi, starList, root + bfn + ".coo")
