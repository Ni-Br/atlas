import args
import os
import fs
import log

pwd = args.pwd
log.i("Indexing " + pwd)
fs.indexFiles(pwd)

log.i("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImageNames(pwd)
if not unprocImgNames or len(unprocImgNames) == 0:
    log.i("No unprocessed images.")
    #TODO stop the program?

log.i("Processing " + str(len(unprocImgNames)) + " images")
for img in unprocImgNames:
    log.d("Getting calbration images for " + img)
    log.v("Getting darks")
    darks = fs.getDarks(pwd, img)
    log.v("Getting biass")
    biass = fs.getBiass(pwd, img)
    log.v("Getting flats")
    flats = fs.getFlats(pwd, img)

    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)

    log.d("IRAF files")
    imgBaseName = os.path.splitext(os.path.basename(img))[0]
    darksFile = open(pwd + ".darks-" + imgBaseName, "w+")
    biassFile = open(pwd + ".biass-" + imgBaseName, "w+")
    flatsFile = open(pwd + ".flats-" + imgBaseName, "w+")
    print(darks, file=darksFile)
    print(biass, file=biassFile)
    print(flats, file=flatsFile)
