import os
import os.path
import fnmatch
import sys
from pyraf import iraf

def reduceBias(bListFn, bMasterFn):
    iraf.imcombine("@" + bListFn, output=bMasterFn, logfile="STDOUT", weight="none", zero="none", reject="crreject", combine="median", scale="none")

iraf.imred()
iraf.ccdred()
def reduceDark(dListFn, dMasterFn, mBiasFn):
    zerocor = "no"
    if os.path.isfile(mBiasFn):
        zerocor = "yes"

    iraf.reset(use_new_imt="no")
    iraf.ccdproc ("@" + dListFn,
            output="", ccdtype=" ", max_cache=0, noproc="no", fixpix="no",
            overscan="no", trim="no", zerocor=zerocor, darkcor="no", flatcor="no", illumcor="no",
            fringecor="no", readcor="no", scancor="no", readaxis="line", fixfile="", biassec="",
            trimsec="", zero=mBiasFn, dark=" ", flat="", illum="", fringe="",
            minreplace=1., scantype="shortscan", nscan=1, interactive="no",
            function="legendre", order=1, sample="*", naverage=1, niterate=1,
            low_reject=3., high_reject=3., grow=0.)

    iraf.imcombine ("@" + dListFn,
            output=dMasterFn, headers="", bpmasks="", rejmasks="", nrejmasks="", expmasks="",
            sigmas="", imcmb="$I", logfile="STDOUT", combine="median", reject="crreject",
            project="no", outtype="real", outlimits="", offsets="none", masktype="none",
            maskvalue="0", blank=0., scale="exposure", zero="none", weight="none",
            statsec="", expname="", lthreshold="INDEF", hthreshold="INDEF", nlow=1, nhigh=1,
            nkeep=1, mclip="yes", lsigma=3., hsigma=3., rdnoise="0.", gain="1.",
            snoise="0.", sigscale=0.1, pclip=-0.5, grow=0.)

def reduceFlat(fListFn, fMasterFn, mBiasFn, mDarkFn):
    zerocor = "no"
    darkcor = "no"
    if os.path.isfile(mBiasFn):
        zerocor = "yes"
    if os.path.isfile(mDarkFn):
        darkcor = "yes"

    print("@" + fListFn)
    print(fMasterFn)
    iraf.ccdproc ("@" + fListFn,
            output="", ccdtype=" ", max_cache=0, noproc="no", fixpix="no",
            overscan="no", trim="no", zerocor=zerocor, darkcor=darkcor, flatcor="no", illumcor="no",
            fringecor="no", readcor="no", scancor="no", readaxis="line", fixfile="", biassec="",
            trimsec="", zero=mBiasFn, dark=mDarkFn, flat="", illum="",
            fringe="", minreplace=1., scantype="shortscan", nscan=1, interactive="no",
            function="legendre", order=1, sample="*", naverage=1, niterate=1,
            low_reject=3., high_reject=3., grow=0.)

    iraf.imcombine("@" + fListFn,
            fMasterFn, headers="", bpmasks="", rejmasks="", nrejmasks="", expmasks="",
            sigmas="", imcmb="$I", logfile="STDOUT", combine="median", reject="crreject",
            project="no", outtype="real", outlimits="", offsets="none", masktype="none",
            maskvalue="0", blank=0., scale="mode", zero="none", weight="none", statsec="",
            expname="", lthreshold="INDEF", hthreshold="INDEF", nlow=1, nhigh=1, nkeep=1,
            mclip="yes", lsigma=3., hsigma=3., rdnoise="0.", gain="1.", snoise="0.",
            sigscale=0.1, pclip=-0.5, grow=0.)

def reduceLight(inFn, outFn, mBiasFn, mDarkFn, mFlatFn):
    flatcor = "no"
    zerocor = "no"
    darkcor = "no"
    if os.path.isfile(mFlatFn):
        flatcor = "yes"
    if os.path.isfile(mBiasFn):
        zerocor = "yes"
    if os.path.isfile(mDarkFn):
        darkcor = "yes"


    iraf.ccdproc (inFn,
            output=outFn, ccdtype=" ", max_cache=0, noproc="no", fixpix="no",
            overscan="no", trim="no", zerocor=zerocor, darkcor=darkcor, flatcor=flatcor, illumcor="no",
            fringecor="no", readcor="no", scancor="no", readaxis="line", fixfile="", biassec="",
            trimsec="", zero=mBiasFn, dark=mDarkFn, flat=mFlatFn, illum="",
            fringe="", minreplace=1., scantype="shortscan", nscan=1, interactive="no",
            function="legendre", order=1, sample="*", naverage=1, niterate=1,
            low_reject=3., high_reject=3., grow=0.)

if __name__ == "__main__":
    iraf.reset(use_new_imt="no")
    root = sys.argv[1]
    print("Root: " + sys.argv[1])
    fitsExt = ".fits"

    bListRgx = ".biass*"
    dListRgx = ".darks*"
    fListRgx = ".flats*"

    bMasterPre = "abm."
    dMasterPre = "adm."
    fMasterPre = "afm."
    lMasterPre = "f."
    print "Bias"
    #Bias 
    listOfBiasLists = [os.path.relpath(os.path.join(dirpath, f), root)
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
        print(fn + "->" + lMasterPre + fn)
        reduceLight(fn, fn + lMasterPre, bMasterFn, dMasterFn, fMasterFn)
