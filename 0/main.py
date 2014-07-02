import args
import fs
import log

tmp = args.tempDir
root = args.root
log.i("Indexing " + root)
fs.indexFiles(root)

log.i("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImageNames(root)
if not unprocImgNames or len(unprocImgNames) == 0:
    log.i("No unprocessed images.")
    #TODO stop the program?

log.i("Processing " + str(len(unprocImgNames)) + " images")
for img in unprocImgNames:
    log.i("Getting calbration images for " + img)
    darks = []
    biass = []
    flats = []
    log.d("Getting darks")
    darks = fs.getDarks(root, img)
    log.d("Getting biass")
    biass = fs.getBiass(root, img)
    log.d("Getting flats")
    flats = fs.getFlats(root, img)
    log.d("Getting darks for flats")
    for flat in flats:
        log.v("Getting darks for flat:" + flat)
        fs.writeListToFile(root + tmp + ".darks-" + flat, fs.getDarks(root, flat))
    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)

    fs.writeListToFile(root + tmp + ".darks-" + imgBaseName, darks)
    fs.writeListToFile(root + tmp + ".biass-" + imgBaseName, biass)
    fs.writeListToFile(root +tmp + ".flats-" + imgBaseName, flats)
