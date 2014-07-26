import os
import subprocess
import sys
#import log
import fnmatch
import fs
import pyfits

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

if __name__ == "__main__":
    exoStarList = getExoplanetList()
    runs = {}
    runFiles = {}
    runOOI = {}
    #get all .corr
    root = sys.argv[1]
    baseFnList = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root))[0]
                        for dirpath, dirnames, files in os.walk(root)
                                    for f in fnmatch.filter(files, "*.solved")]
    baseFnList.sort()

    for bfn in baseFnList:
        print("opening " + bfn)
        hdr = fs.getHeader(bfn + ".new")
        date = hdr["DATE-OBS"].split("T")[0]

        wcsList = [i.split(" ") for i in fs.readFileToArray(bfn + ".wcs.center")]
        wcsDict = {}
        for key, value in wcsList:
            wcsDict[key] = value

        ooi = {}
        starNotFound = True
        for exoStar in exoStarList:
            if areEqual(exoStar["ra"], wcsDict["ra_center"], 0.166) and areEqual(exoStar["dec"], wcsDict["dec_center"], 0.166):
                starNotFound = False
                ooi = exoStar
                print("the star is: " + ooi["name"])

        if starNotFound:
            print("404 - STAR NOT FOUND: " + bfn)
            continue

        f = pyfits.open(bfn + ".rdls")
        rdSources = f[1].data

        index = date + ooi["name"]
        #TODO use sets
        #TODO use columns instead of 0 and 1
        if index in runs:
            runFiles[index].append(bfn)
            temp = []
            print(len(runs[index]))
            count = 0
            for i in runs[index]:
                for j in rdSources:
                    if areEqual(i[0], j[0]) and areEqual(i[1], j[1]):
                        exists =  False
                        for k in temp:
                            if areEqual(i[0], k[0]) and areEqual(k[1], i[1]):
                                exists = True
                        if not exists:
                            #print(str(i[0]) + ", " + str(j[0]))
                            count += 1
                            temp.append(i)
            #print(count)
            runs[index] = temp
        else:
            runs[index] = rdSources
            runFiles[index] = [bfn]
            runOOI[index] = ooi

    #for index in runs:
        #print(index)
        #print(runs[index])
        #print(runFiles[index])

    for index in runs:
        fs.writeListToFile(root + index + ".atlas.rdls", runs[index])
        for bfn in runFiles[index]:
            try:
                output = subprocess.check_output(["wcs-rd2xy", "-w", bfn + ".wcs", "-r", str(runOOI[index]["ra"]), "-d", str(runOOI[index]["dec"])])
            except subprocess.CalledProcessError as e:
                print("wcs-rd2xy:" + str(e.output))
            output = str(output)

            #ouput format is RA,Dec (val, val) -> pixel (val, val)
            output = output.split(">")[1]
            output = output.split("(")[1]
            x = output.split(",")[0]
            y = output.split(" ")[1]
            y = y.split(")")[0]
            coords = [str(x) + " " + str(y)]
            for ra, dec in runs[index]:
                if areEqual(ra, runOOI[index]["ra"]) and areEqual(dec, runOOI[index]['dec']):
                    continue
                try:
                    output = subprocess.check_output(["wcs-rd2xy", "-w", bfn + ".wcs", "-r", str(ra), "-d", str(dec)])
                except subprocess.CalledProcessError as e:
                    print("wcs-rd2xy:" + str(e.output))

                output = str(output)
                #ouput format is RA,Dec (val, val) -> pixel (val, val)
                output = output.split(">")[1]
                output = output.split("(")[1]
                x = output.split(",")[0]
                y = output.split(" ")[1]
                y = y.split(")")[0]
                print(x + " " + y)
                coords.append(str(x) + " " + str(y))

            fs.writeListToFile(root + bfn + ".new.coo", coords)
