import os
import logging
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

def addDataToPlt(plt, dates, diff, c = 'w'):
    fig, ax = plt.subplots()
    diff3 = [i for i in diff]
    diff7 = [i for i in diff]
    for i in range(3, len(diff) - 4):
        s = 0
        for j in range(i - 3, i+4):
            s += diff[j]
        diff7[i] = s/7 
    for i in range(1, len(diff) - 2):
        s = 0
        for j in range(i - 1, i+2):
            s += diff[j]
        diff3[i] = s/3 
        
    ax.plot_date(dates, diff, c, xdate=True, marker = "o", linestyle="", label="raw")
    ax.plot_date(dates, diff3, 'b', xdate=True, marker = ".", linestyle="", label="avg3")
    ax.plot_date(dates, diff7, 'r', xdate=True, marker = ".", linestyle="", label="avg7")
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:00"))
    ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator())
    ax.autoscale_view()
    fig.autofmt_xdate()
    plt.legend()

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
        appertures = split[0][int((len(split[0])+1) / 2):]
        data = [[], []]
        #This creates an array in the format data[star][field][exp]
        for line in split:
            app = line[1:int((len(line)+1)/2)]
            starId = int(line[0])
            if len(data) <= starId:
                data.append([app])
            else:
                data[starId].append(app)

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
            addDataToPlt(plt, dates, magDifByExp[i], "w")
            plt.xlabel('Time')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(root + os.path.splitext(fn)[0] + "-" + str(int(float(appertures[i]))) + ".png", dpi=180)
            plt.close()

        for i in range(len(magDifByExp)):
            addDataToPlt(plt, dates, magDifByExp[i], colorList[i])
        plt.xlabel('Timestamp (seconds)')
        plt.ylabel('Apparent magnitude difference')
        plt.savefig(root + os.path.splitext(fn)[0] + ".png", dpi = 180)
        plt.close()
        logger.info("Done")
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
