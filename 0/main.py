import fs
import log
import pyfits
import argparse
import fnmatch
import os

parser = argparse.ArgumentParser()
parser.add_argument("dir", default=".", help="Search for images in specified directory")
parser.add_argument("-l", "--log", default=".atlas_0.log", help="Specifies the location of the log file, default is dir/.atlas_0.log")
parser.add_argument("-s", "--summary", default=".atlas_0.sum", help="Specifies location of for the summary of all decisions made, default is dir/atlas_0.sum")
parser.add_argument("-t", "--temp", default="atlas_0/", help="Specifies the directory in which files sent to atlas_1 will be stored")
parser.add_argument("-v", "--verbose", action="store_true", help="Outputs contents of log to stdout as well as to the log file")
parser.add_argument("--log-level", type=int, default=3, help="Sets the level of logging that is recorded: 0=error, 1=warning, 2=information, 3=debug, 4=verbose. It is impossible to set it below 0.")

args = parser.parse_args()
pwd = os.path.dirname(args.dir)
log = log.Log(args.log, args.log_level, True)

#TODO Check if this is a vulnerability of some kind
log.i("Setting directory to " + args.dir)
os.chdir(args.dir)


log.v("Getting all .fits in directories and sub-dirs")
fitsFiles = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(args.dir)
        for f in fnmatch.filter(files, "*.fit*")]
log.v("Files are:")
#print(fitsFiles)

FS = fs.FS(pwd, log)
fs.addList(fitsFiles, FS)
unproc = FS.getUnprocessedImages()
for img in unproc:
    #log.d(img)

    #log.d("Getting calibration images for " + img['_id'])
    print "Getting calibration images for " + img['_id']
    darks = FS.getDarks(img)
    biass = FS.getBiass(img)
    flats = FS.getFlats(img)
    log.v("Darks")
    for dark in darks:
        print dark['_id']
    log.v("Biass")
    for bias in biass:
        print bias['_id']
    log.v("Flats")
    for flat in flats:
        print flat['_id']
