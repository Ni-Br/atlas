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
biassFiles = {}
darksFiles = {}
flatsFiles = {}

for img in unprocImgNames:
    log.i("Getting calbration images for " + img)
    hdr = fs.getHeader(root + img)
    exptime = hdr['EXPTIME']
    date = hdr['DATE-OBS'].split('T')
    date = date[0]
    datexp = date + ":" + str(exptime)
    #Darks
    if date in darksFiles:
        log.d("Darks file already exists")
        darksFiles[date].append(img)
    else:
        log.d("Getting darks")
        darks = fs.getDarks(root, img)
        darksFiles[date] = [img]
        if len(darks) > 0:
            fs.writeListToFile(root + tmp + ".darks:" + date, darks)
    #Biass
    if date in biassFiles:
        log.d("Biass file already exists")
        biassFiles[date].append(img)
    else:
        log.d("Getting biass")
        biass = fs.getBiass(root, img)
        biassFiles[date] = [img]
        if len(biass) > 0:
            fs.writeListToFile(root + tmp + ".biass:" + date, biass)
    #Flats
    if date in flatsFiles:
        log.d("Flats file already exists")
        flatsFiles[date].append(img)
    else:
        log.d("Getting flats")
        flats = fs.getFlats(root, img)
        flatsFiles[date] = [img]
        if len(flats) > 0:
            fs.writeListToFile(root +tmp + ".flats:" + date, flats)
    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)

listFlats = fs.getAllFlats(root)
log.i("Getting darks for flats")
for flat in listFlats:
    log.i("Getting calbration images for " + flat)
    hdr = fs.getHeader(root + flat)
    date = hdr['DATE-OBS'].split('T')
    date = date[0]
    if date in darksFiles:
        log.d("Darks file already exists")
        darksFiles[date].append(flat)
    else:
        log.d("Getting darks")
        darks = fs.getDarks(root, flat)
        darksFiles[date] = [flat]
        if len(darks) > 0:
            fs.writeListToFile(root + tmp + ".darks:" + date, darks)
