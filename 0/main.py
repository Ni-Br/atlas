import fs
import log
import pyfits
import argparse
import fnmatch
import os

parser = argparse.ArgumentParser()
parser.add_argument("dir", default=".", help="Search for images in specified directory")
parser.add_argument("-s", "--summary", default=".atlas_0.sum", help="Specifies location of for the summary of all decisions made, default is dir/atlas_0.sum")
parser.add_argument("-t", "--temp", default="atlas_0/", help="Specifies the directory in which files sent to atlas_1 will be stored")
parser.add_argument("-v", "--verbose", action="store_true", help="Outputs contents of log to stdout as well as to the log file")
parser.add_argument("--log-level", type=int, default=3, help="Sets the level of logging that is recorded: 0=error, 1=warning, 2=information, 3=debug, 4=verbose. It is impossible to set it below 0.")

args = parser.parse_args()
log = log.Log(args.log, args.log_level, True)


#log.v("Getting all .fits in directories and sub-dirs")
#fitsFiles = [os.path.join(dirpath, f)
#        for dirpath, dirnames, files in os.walk(args.dir)
#        for f in fnmatch.filter(files, "*.fit*")]
log.i("Indexing " + args.dir)
fs.indexFiles(args.dir)
#log.v("Files are:")
#print(fitsFiles)

log.i("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImages()
if len(unprocImgNames) == 0:
    log.i("No unprocessed images.")
    #TODO stop the program?

log.i("Processing " + len(unprocImgNames) + " images")
for img in unprocImgNames:
    log.d("Getting calbration images for ".format(img))
    log.v("Getting darks")
    darks = fs.findDarks(img)
    log.v("Getting biass")
    biass = fs.findBiass(img)
    log.v("Getting flats")
    flats = fs.findFlats(img)

    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)

    log.d("IRAF files")
    print(darks, file="atlas-d."+img)
    print(biass, file="atlas-b."+img)
    print(flats, file="atlas-f."+img)
