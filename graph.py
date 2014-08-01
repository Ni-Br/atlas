import os
import loggin
import sys
import fnmatch
import datetime
import fs
import numpy as np
import matplotlib
#To disable X, has to be imported before pyplot
matplotlib.use('Agg')

import matplotlib.pyplot as plt

colorList = ['c', 'b', 'm', 'r', 'y', 'g', 'w', 'k']
colorList+=colorList
colorList+=colorList
colorList+=colorList

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    root = sys.argv[1]
    resFnList = [os.path.relpath(os.path.join(dirpath, f), root)
                    for dirpath, dirnames, files in os.walk(root)
                        for f in fnmatch.filter(files, "*.res")]
    resFnList.sort()

    for fn in resFnList:
        logger.info("Working on " + fn)
        array = fs.readFileToArray(root + fn)
        split = [i.split()[:-1] for i in array]
        times = [i.split()[-1] for i in array]
        data = [[], []]
        #This creates an array in the format data[star][field][exp]
        for line in split:
            if len(data)<=int(line[0]):
                data.append([line[2:]])
            else:
                data[int(line[0])].append(line[2:])
        nbStars = len(data) - 1 #Because star 0 doesn't exist, silly IRAF
        nbFields = len(data[1])
        nbExp = len(data[1][0])
        times = times[::nbStars]
        timestamps = [datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=datetime.timezone.utc) for i in times]

        goodStarsByExp = [[] for i in range(nbExp)]
        for exp in range(nbExp):
            for star in range(1, nbStars + 1):
                isIndef = False
                for field in range(nbFields):
                    if isIndef or data[star][field][exp] == "INDEF":
                        isIndef = True
                        break
                if not isIndef:
                    goodStarsByExp[exp].append(star)

        for goodStars in goodStarsByExp:
            logger.debug(goodStars)


        timeAxis = []
        magDifByExp = []
        diffDone = False
        for exp in range(nbExp):
            stars = goodStarsByExp[exp]
            if 1 not in stars:
                continue
            diffDone = True
            nbStars = len(stars)
            magdif = []
            for field in range(nbFields):
                photSum = 0
                for star in stars:
                    val = data[star][field][exp]
                    if val != "INDEF":
                        photSum += float(val)
                    else:
                        logger.error("INDEF!" + str(star) + " " + str(time[field]))
                magdif.append(photSum/nbStars - float(data[1][field][exp]))
            magDifByExp.append(magdif)
        if not diffDone:
            logger.warning("Sad transit: " + fn)
            continue

        dates = matplotlib.dates.date2num(timestamps)
        for i in range(len(magDifByExp)):
            plt.scatter(dates, magDifByExp[i], c=colorList[i])
            plt.xlabel('Timestamp (seconds)')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(root + os.path.splitext(fn)[0] + "-" + str(i) + ".png")
            plt.close()

        print("Next stage")
        for i in range(len(magDifByExp)):
            plt.scatter(dates, magDifByExp[i], c=colorList[i])
        plt.xlabel('Timestamp (seconds)')
        plt.ylabel('Apparent magnitude difference')
        plt.savefig(root + os.path.splitext(fn)[0] + ".png")
        plt.close()
        print("Done")
        #*****************Plot 'expected' start/mid/end of transit
        ##difaver = 0.65  #!!!INPUT!!!: run program for first time, look at average value of y-axis, input,
                            #then uncomment this line and the 3 lines below to plot.
        #start = 9180 #INPUT
        #mid = 11640  #INPUT
        #end = 14100  #INPUT
        ##plt.plot([start,start], [difaver+0.05, difaver-0.05], color='r', linestyle='-', linewidth=2)
        ##plt.plot([mid,mid], [difaver+0.05, difaver-0.05], color='r', linestyle='-', linewidth=2)
        ##plt.plot([end,end],[difaver+0.05, difaver-0.05], color='r', linestyle='-', linewidth=2)
        #*************************************************
