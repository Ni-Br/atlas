##Credit to Duy Anh N Doan <ddoan@mit.edu> for the skeleton of the script
import statistics as stats
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

colorList = ['c', 'b', 'm', 'r', 'y', 'g', 'k']
colorList+=colorList
colorList+=colorList
colorList+=colorList

def addDataToPlt(fig, ax, dates, diff, c = 'c', label="raw", isMultiple=True):
    label1 = "average of 3"
    label2 = "average of 7"

    med3 = [i for i in diff]
    med7 = [i for i in diff]
    diff3 = [i for i in diff]
    diff7 = [i for i in diff]
    for i in range(3, len(diff) - 4):
        if i > 2 and i < len(diff) - 4:
            diff7[i] = stats.mean(diff[i-3:i+4])
            med7[i] = stats.median(diff[i-3:i+3])
        if i > 0 and i < len(diff) - 2:
            diff3[i] = stats.mean(diff[i-1:i+2])
            med3[i] = stats.median(diff[i-1:i+2])
        
    marker = "o"
    if len(diff) > 200:
        marker = "."
    if not isMultiple:
        if stats.stdev(diff) > 0.1:
            marker = "x"

    ax.plot_date(dates, diff, c, xdate=True, marker = marker, linestyle="", label=label)
    #ax.plot_date(dates, avg3, 'b', xdate=True, marker = ".", linestyle="", label=label1)
    #ax.plot_date(dates, avg7, 'r', xdate=True, marker = ".", linestyle="", label=label2)
    if isMultiple:
        ax.plot_date(dates, med3, 'b', xdate=True, marker = ".", linestyle="", label=label1)
        ax.plot_date(dates, med7, 'r', xdate=True, marker = ".", linestyle="", label=label2)
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:00"))
    ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator())
    ax.autoscale_view()
    fig.autofmt_xdate()
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    root = sys.argv[1]
    resFnList = [os.path.relpath(os.path.join(dirpath, f), root)
                    for dirpath, dirnames, files in os.walk(root)
                        for f in fnmatch.filter(files, "*.res")]
    resFnList.sort()

    dest = root + "graph/"
    if not os.path.exists(dest):
        os.makedirs(dest)

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
        magDifByExpStar = []
        diffDone = False
        for exp in range(nbExp):
            stars = goodStarsByExp[exp]
            if 1 not in stars:
                continue
            diffDone = True
            magdifByStar = {}
            for star in stars:
                magdifByStar[star] = []

            for field in range(nbFields):
                vals = []
                for star in stars:
                    vals.append(float(data[star][field][exp]))
                for i in range(len(stars)):
                    star = stars[i]
                    magdifByStar[star].append(stats.mean(vals[1:i] + vals[i+1:]) - float(data[star][field][exp]))

            magDifByExpStar.append(magdifByStar)
        if not diffDone:
            logger.warning("Sad transit: " + fn)
            continue

        dpi = 150

        if not os.path.exists(dest + "comp/"):
            os.makedirs(dest + "comp/")

        dates = matplotlib.dates.date2num(timestamps)
        for i in range(len(magDifByExpStar)):
            fig, ax = plt.subplots()
            app = str(int(float(appertures[i])))
            logger.debug("Plot " + app)
            addDataToPlt(fig, ax, dates, magDifByExpStar[i][1], "c", app)
            plt.xlabel('Time')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(dest + os.path.splitext(fn)[0] + "-" + app + ".png", dpi=dpi, bbox_extra_artists=(ax.legend,))
            plt.close()

            ##Other stars, by app
            fig, ax = plt.subplots()
            logger.debug("Plot " + app + " comparison stars")
            for star in goodStarsByExp[i]:
                addDataToPlt(fig, ax, dates, magDifByExpStar[i][star], colorList[star], star, False)
                #print(str(star) + ": " + str(stats.median(magDifByExpStar[i][star])) + "," + str(stats.stdev(magDifByExpStar[i][star])))
            sys.stdout.flush()
            plt.xlabel('Time')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(dest + "comp/" + os.path.splitext(fn)[0] + "-" + app + ".comparison.png", dpi=dpi, bbox_extra_artists=(ax.legend,))
            plt.close()

        fig, ax = plt.subplots()
        logger.debug("Plot collective")
        for i in range(len(magDifByExpStar)):
            app = str(int(float(appertures[i])))
            addDataToPlt(fig, ax, dates, magDifByExpStar[i][1], colorList[i], app, False)

        plt.xlabel('Timestamp (seconds)')
        plt.ylabel('Apparent magnitude difference')
        plt.savefig(dest + os.path.splitext(fn)[0] + ".png", dpi = dpi, bbox_extra_artists=(ax.legend(),), bbox_inches='tight')
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
