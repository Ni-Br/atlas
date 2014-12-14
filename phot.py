import os
import logging
import os.path
import fnmatch
import sys
from pyraf import iraf

#TODO actually set aperture and stuff
def phot(fn, outFn):
    if os.path.isfile(outFn):
        logger.debug("Skip, " + outFn + " exists!")
        return

    home = os.path.expanduser("~")

    iraf.centerpars.setParam("cbox", 3)
    iraf.centerpars.saveParList(filename= home + "/uparm/aptcentes.par")

    iraf.fitskypars.setParam("annulus", 30)
    iraf.fitskypars.setParam("dannulus", 5)
    iraf.fitskypars.saveParList(filename= home + "/uparm/aptfitsks.par")
            
    iraf.photpars.setParam("apertur", ', '.join(str(i) for i in range(3, 25, 2)))
    iraf.photpars.setParam("zmag", 25)
    iraf.photpars.saveParList(filename= home + "/uparm/aptphot.par")

    cooFile = fn + ".coo"
    iraf.phot(fn, coords =  cooFile, output = outFn, interac = "no", verify = "no", Stdout=1, cbox=3,
            exposur = "EXPTIME", airmass = "AIRMASS", filter = "DATE-OBS", #To keep it as a string
            apertur = "3, 6, 9, 12, 15, 18, 21", annulus = 40, dannulus = 5, obstime = "")

if __name__ == "__main__":
    iraf.imred()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    #iraf.reset(use_new_imt="no")
    root = sys.argv[1]
    logger.info("Root: " + sys.argv[1])
    fitsExt = ".fits"

    cooFnRgx = "*.coo"

    bfns = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root))[0]
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, cooFnRgx)]
    bfns.sort()

    for bfn in bfns:
        logger.debug("Doing photometry on " + bfn)
        phot(root + bfn, root + bfn + ".mag")

    txdmpFnRgx = "*.txdmp"
    txdmpFns = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, txdmpFnRgx)]
    txdmpFns.sort()

    for fn in txdmpFns:
        #txdump *.mag.1 image,id,mag,otime yes > output.txt
        iraf.txdump(textfiles = "@" + root + fn, fields= "id,mag,rapert,ifilter", expr =  "yes", Stdout = root + fn + ".res")
