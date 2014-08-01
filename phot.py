import os
import logging
import os.path
import fnmatch
import sys
from pyraf import iraf

#TODO actually set aperture and stuff
def phot(fn, outFn):
    if os.path.isfile(fn):
        return

    cooFile = fn + ".coo"
    iraf.phot(fn, coords =  cooFile, output = outFn, interac = "no", verify = "no", Stdout=0,
            eposur = "exptime", filter = "filter", apertur = "5, 10, 15, 20, 25, 30", annulus = 40,
            dannulus = 5, gain = 1, obstime = "date-obs")

iraf.imred()

if __name__ == "__main__":
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
        iraf.txdump(textfiles = "@" + root + fn, fields= "id,mag,ifilter", expr =  "yes", Stdout = root + fn + ".res")
