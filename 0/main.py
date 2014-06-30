import args
import fs
import log

#log.v("Getting all .fits in directories and sub-dirs")
#fitsFiles = [os.path.join(dirpath, f)
#        for dirpath, dirnames, files in os.walk(args.pwd)
#        for f in fnmatch.filter(files, "*.fit*")]
log.i("Indexing " + args.pwd)
fs.indexFiles(args.pwd)
#log.v("Files are:")
#print(fitsFiles)

log.i("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImageNames(args.pwd)
if not unprocImgNames or len(unprocImgNames) == 0:
    log.i("No unprocessed images.")
    #TODO stop the program?

log.i("Processing " + str(len(unprocImgNames)) + " images")
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
