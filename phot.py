import os
import os.path
import fnmatch
import sys
from pyraf import iraf

#TODO actually set aperture and stuff
def phot(bfn, outFn):
    cooFile = bfn + ".coo"
    bfn += ".new"
    iraf.phot(bfn, coords =  cooFile, output = outFn, interac = "no", verify = "no", Stdout=1)

iraf.imred()

if __name__ == "__main__":
    #iraf.reset(use_new_imt="no")
    root = sys.argv[1]
    print("Root: " + sys.argv[1])
    fitsExt = ".fits"

    cooFnRgx = "*.coo"

    bfns = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root))[0]
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, cooFnRgx)]
    bfns.sort()

    for bfn in bfns:
        print("Doing photometry on " + bfn)
        phot(bfn, "atlas_" + bfn + ".mag")
