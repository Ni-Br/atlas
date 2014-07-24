import os
import os.path
import fnmatch
import sys
from pyraf import iraf

def reduceBias(bListFn, bMasterFn):
    iraf.imcombine("@" + bListFn, output=bMasterFn, logfile="STDOUT", weight="none", zero="none", reject="crreject", combine="median", scale="none")

iraf.imred()

if __name__ == "__main__":
    iraf.reset(use_new_imt="no")
    root = sys.argv[1]
    print("Root: " + sys.argv[1])
    fitsExt = ".fits"

    cooFnRgx = ".coo*"

    print "Bias"
    #Bias 
    cooFns = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, bListRgx)]

    print(listOfBiasLists)
    for bListFile in listOfBiasLists:
        print "Bias:", bListFile
        date = bListFile.split(":")[1]
        reduceBias(root + bListFile, bMasterPre + date)

    #Dark
    listOfDarkLists = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, dListRgx)]

    print "DARK"
    print(listOfDarkLists)
    for dListFile in listOfDarkLists:
        print(dListFile)
        date = dListFile.split(":")[1]
        bMasterFn = bMasterPre + date + fitsExt
        reduceDark(root + dListFile, dMasterPre + date, bMasterFn)
    
    #Flat
    listOfFlatLists = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, fListRgx)]

    print "Flat"
    print(listOfFlatLists)
    for fListFile in listOfFlatLists:
        print(fListFile)
        date = fListFile.split(":")[1]
        bMasterFn = bMasterPre + date + fitsExt
        dMasterFn = dMasterPre + date + fitsExt
        reduceFlat(root + fListFile, fMasterPre + date, bMasterFn, dMasterFn)

    #Light
    lListFile = open(".lights")
    lList = [line.strip('\n') for line in lListFile]
    
    print "Light"
    print(lList)
    for light in lList:
        fn = light.split(":")[0]
        date = light.split(":")[1]
        bMasterFn = bMasterPre + date + fitsExt
        dMasterFn = dMasterPre + date + fitsExt
        fMasterFn = fMasterPre + date + fitsExt
        print(fn + "->" + fn + lMasterPre)
        reduceLight(fn, fn + lMasterPre, bMasterFn, dMasterFn, fMasterFn)
