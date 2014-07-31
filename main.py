import args
import fs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(name)s %(asctime)s %(message)s')
logger = logging.getLogger(__name__)

tmp = args.tempDir
root = args.root
logger.info("Indexing " + root)
fs.indexFiles(root)

logger.info("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImageNames(root)
if not unprocImgNames or len(unprocImgNames) == 0:
    logger.info("No unprocessed images.")
    #TODO stop the program?
unprocImgNames.sort()

logger.info("Processing " + str(len(unprocImgNames)) + " images")
biassFiles = {}
darksFiles = {}
flatsFiles = {}
procFiles = fs.readFileToArray(root + ".proc")

for img in unprocImgNames:
    logger.debug("Getting calibration images for " + img)
    hdr = fs.getHeader(root + img)
    exptime = hdr['EXPTIME']
    date = hdr['DATE-OBS'].split('T')
    date = date[0]
    datexp = date + ":" + str(exptime)
    #Darks
    if date in darksFiles:
        logger.debug("Darks file already exists")
        darksFiles[date].append(img)
    else:
        logger.debug("Getting darks")
        darks = fs.getDarks(root, img)
        darksFiles[date] = [img]
        if len(darks) > 0:
            fs.writeListToFile(root + tmp + ".debugarks:" + date, darks)
    #Biass
    if date in biassFiles:
        logger.debug("Biass file already exists")
        biassFiles[date].append(img)
    else:
        logger.debug("Getting biass")
        biass = fs.getBiass(root, img)
        biassFiles[date] = [img]
        if len(biass) > 0:
            fs.writeListToFile(root + tmp + ".biass:" + date, biass)
    #Flats
    if date in flatsFiles:
        logger.debug("Flats file already exists")
        flatsFiles[date].append(img)
    else:
        logger.debug("Getting flats")
        flats = fs.getFlats(root, img)
        flatsFiles[date] = [img]
        if len(flats) > 0:
            fs.writeListToFile(root +tmp + ".flats:" + date, flats)
    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)
    procFiles.append(img)

listFlats = fs.getUnprocessedFlatFn(root)
logger.info("Getting darks for flats")
for flat in listFlats:
    logger.debug("Getting calbration images for " + flat)
    hdr = fs.getHeader(root + flat)
    date = hdr['DATE-OBS'].split('T')
    date = date[0]
    if date in darksFiles:
        logger.debug("Darks file already exists")
        darksFiles[date].append(flat)
    else:
        logger.debug("Getting darks")
        darks = fs.getDarks(root, flat)
        darksFiles[date] = [flat]
        if len(darks) > 0:
            fs.writeListToFile(root + tmp + ".darks:" + date, darks)
    procFiles.append(flat)

fs.writeListToFile(root + ".proc", procFiles)
