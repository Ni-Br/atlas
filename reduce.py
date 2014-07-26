import os
import os.path
import fnmatch
import sys
from pyraf import iraf

def reduceBias(bListFn, bMasterFn):
    if not os.path.isfile(bMasterFn + ".fits"):
        iraf.imcombine("@" + bListFn, output=bMasterFn, logfile="STDOUT", weight="none", zero="none", reject="crreject", combine="median", scale="none")

def reduceDark(dListFn, dMasterFn, mBiasFn):
    if os.path.isfile(dMasterFn + ".fits"):
        return

    zerocor = "no"
    if os.path.isfile(mBiasFn + ".fits"):
        zerocor = "yes"

    print("File list: @" + dListFn)
    print("dMasterFn: " + dMasterFn)
    iraf.reset(use_new_imt="no")
    iraf.ccdproc ("@" + dListFn,
            output="@" + dListFn + "//atlas_b", ccdtype=" ", max_cache=0, noproc="no", fixpix="no",
            overscan="no", trim="no", zerocor=zerocor, darkcor="no", flatcor="no", illumcor="no",
            fringecor="no", readcor="no", scancor="no", readaxis="line", fixfile="", biassec="",
            trimsec="", zero=mBiasFn, dark=" ", flat="", illum="", fringe="",
            minreplace=1., scantype="shortscan", nscan=1, interactive="no",
            function="legendre", order=1, sample="*", naverage=1, niterate=1,
            low_reject=3., high_reject=3., grow=0.)

    iraf.imcombine ("@" + dListFn + "//atlas_b",
            output=dMasterFn, headers="", bpmasks="", rejmasks="", nrejmasks="", expmasks="",
            sigmas="", imcmb="$I", logfile="STDOUT", combine="median", reject="crreject",
            project="no", outtype="real", outlimits="", offsets="none", masktype="none",
            maskvalue="0", blank=0., scale="exposure", zero="none", weight="none",
            statsec="", expname="", lthreshold="INDEF", hthreshold="INDEF", nlow=1, nhigh=1,
            nkeep=1, mclip="yes", lsigma=3., hsigma=3., rdnoise="0.", gain="1.",
            snoise="0.", sigscale=0.1, pclip=-0.5, grow=0.)

def reduceFlat(fListFn, fMasterFn, mBiasFn, mDarkFn):
    if os.path.isfile(fMasterFn + ".fits"):
        return
    zerocor = "no"
    darkcor = "no"
    if os.path.isfile(mBiasFn + ".fits"):
        zerocor = "yes"
    if os.path.isfile(mDarkFn + ".fits"):
        darkcor = "yes"

    #print("@" + fListFn)
    #print(fMasterFn)
    iraf.ccdproc ("@" + fListFn,
            output="@" + fListFn + "//atlas_bd", ccdtype=" ", max_cache=0, noproc="no", fixpix="no",
            overscan="no", trim="no", zerocor=zerocor, darkcor=darkcor, flatcor="no", illumcor="no",
            fringecor="no", readcor="no", scancor="no", readaxis="line", fixfile="", biassec="",
            trimsec="", zero=mBiasFn, dark=mDarkFn, flat="", illum="",
            fringe="", minreplace=1., scantype="shortscan", nscan=1, interactive="no",
            function="legendre", order=1, sample="*", naverage=1, niterate=1,
            low_reject=3., high_reject=3., grow=0.)

    iraf.imcombine("@" + fListFn + "//atlas_bd",
            fMasterFn, headers="", bpmasks="", rejmasks="", nrejmasks="", expmasks="",
            sigmas="", imcmb="$I", logfile="STDOUT", combine="median", reject="crreject",
            project="no", outtype="real", outlimits="", offsets="none", masktype="none",
            maskvalue="0", blank=0., scale="mode", zero="none", weight="none", statsec="",
            expname="", lthreshold="INDEF", hthreshold="INDEF", nlow=1, nhigh=1, nkeep=1,
            mclip="yes", lsigma=3., hsigma=3., rdnoise="0.", gain="1.", snoise="0.",
            sigscale=0.1, pclip=-0.5, grow=0.)

def reduceLight(inFn, outFn, mBiasFn, mDarkFn, mFlatFn):
    if os.path.isfile(outFn + ".fits"):
        return
    print(fn + " -> " + outFn)
    flatcor = "no"
    zerocor = "no"
    darkcor = "no"
    if os.path.isfile(mFlatFn + ".fits"):
        flatcor = "yes"
    if os.path.isfile(mBiasFn + ".fits"):
        zerocor = "yes"
    if os.path.isfile(mDarkFn + ".fits"):
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
    iraf.imred()
    iraf.ccdred()

    root = sys.argv[1]
    atlas0 = "atlas_0/"
    print("Root: " + sys.argv[1])
    os.chdir(root)
    fitsExt = ".fits"

    bListRgx = ".biass*"
    dListRgx = ".darks*"
    fListRgx = ".flats*"

    dataFolder = "atlas_1/"
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)
    bMasterPre = dataFolder + "abm."
    dMasterPre = dataFolder + "adm."
    fMasterPre = dataFolder + "afm."
    lMasterPre = dataFolder + "light/"
    if not os.path.exists(lMasterPre):
        os.makedirs(lMasterPre)

    print "Bias"
    #Bias 
    listOfBiasLists = [os.path.relpath(os.path.join(dirpath, f), atlas0)
            for dirpath, dirnames, files in os.walk(atlas0)
            for f in fnmatch.filter(files, bListRgx)]
    listOfBiasLists.sort()

    #print(listOfBiasLists)
    for bListFile in listOfBiasLists:
        print "Bias:", bListFile
        date = bListFile.split(":")[1]
        reduceBias(atlas0 + bListFile, bMasterPre + date)

    #Dark
    listOfDarkLists = [os.path.relpath(os.path.join(dirpath, f), atlas0)
            for dirpath, dirnames, files in os.walk(atlas0)
            for f in fnmatch.filter(files, dListRgx)]
    listOfDarkLists.sort()

    print "DARK"
    #print(listOfDarkLists)
    for dListFile in listOfDarkLists:
        print(dListFile)
        date = dListFile.split(":")[1]
        bMasterFn = bMasterPre + date
        reduceDark(atlas0 + dListFile, dMasterPre + date, bMasterFn)
    
    #Flat
    listOfFlatLists = [os.path.relpath(os.path.join(dirpath, f), atlas0)
            for dirpath, dirnames, files in os.walk(atlas0)
            for f in fnmatch.filter(files, fListRgx)]
    listOfFlatLists.sort()

    print "Flat"
    #print(listOfFlatLists)
    for fListFile in listOfFlatLists:
        print(fListFile)
        date = fListFile.split(":")[1]
        bMasterFn = bMasterPre + date
        dMasterFn = dMasterPre + date
        reduceFlat(atlas0 + fListFile, fMasterPre + date, bMasterFn, dMasterFn)

    #Light
    lListFile = open(".lights")
    lList = [line.strip('\n') for line in lListFile]
    lList.sort()
    
    print "Light"
    #print(lList)
    for light in lList:
        fn = light.split(":")[0]
        bfn = os.path.splitext(fn)[0]
        date = light.split(":")[1]
        bMasterFn = bMasterPre + date
        dMasterFn = dMasterPre + date
        fMasterFn = fMasterPre + date
        outFn = lMasterPre + bfn
        if not os.path.exists(outFn):
            os.makedirs(outFn)
        reduceLight(fn, outFn, bMasterFn, dMasterFn, fMasterFn)
