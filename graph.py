##Credit to Duy Anh N Doan <ddoan@mit.edu> for the skeleton of the script
import csv
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

#data[star][field]
def analyzeTransitByApp(data, stars):
    assert len(data) == len(stars), __name__ + "analyzeTransitByApp(): data and stars are not the same length"
    
    magdifByStar = {}
    for star in stars:
        magdifByStar[star] = []

    for field in range(len(data[0])):
        vals = []
        for star in range(len(stars)):
            vals.append(float(data[star][field]))

        for i, star in enumerate(stars):
            #To not do the difference to the comp star if there is only one...
            if len(stars[1:]) >= 2:
                magdifByStar[star].append(stats.mean(vals[1:i] + vals[i+1:]) - vals[i])
            else:
                magdifByStar[star].append(vals[i])

    return magdifByStar

def getTransitStartEnd(index):
    reader = csv.reader(open("/home/astron/bin/atlas/transits.cgi"))
    target, date = index.split(".")

    dateSplit = date.split("-")
    dateMDY = dateSplit[1] + "-" + dateSplit[2] + "-" + dateSplit[0]

    target = target.replace("-", "").lower()
    logger.debug("Looking for " + target + " " + date)

    found = False
    start, end = ("", "")
    for line in reader:
        lineTarget = line[0].replace("-", "").replace(" ", "").lower()

        if target in lineTarget and dateMDY in line[3]:
            start = line[1] + "," + line[2]
            end = line[3] + "," + line[4]
            logger.debug("Start: " + str(start) + ", End: " + str(end))

            start = datetime.datetime.strptime(start, "%m-%d-%Y,%H:%M").replace(tzinfo=datetime.timezone.utc)
            end = datetime.datetime.strptime(end, "%m-%d-%Y,%H:%M").replace(tzinfo=datetime.timezone.utc)
            
            found = True

    if not found:
        logger.warning("Transit not found!")
        return ("", "")

    start, end = matplotlib.dates.date2num((start, end))
    return (start, end)

def addStartEndToPlt(ax, startEnd):
    start, end = startEnd
    if start != "":
        ax.axvline(start, color = 'r', zorder=0)
    if end != "":
        ax.axvline(end, color = 'b', zorder=0)


def addDataToPlt(fig, ax, dates, diff, c = 'c', label="raw", isMultiple=True):
    assert len(dates) == len(diff), "Plot and data are of different lenght"
    label1 = "average of 3"
    label2 = "average of 7"

    med3 = [i for i in diff]
    med7 = [i for i in diff]
    for i in range(3, len(diff) - 4):
        if i > 2 and i < len(diff) - 4:
            med7[i] = stats.median(diff[i-3:i+3])
        if i > 0 and i < len(diff) - 2:
            med3[i] = stats.median(diff[i-1:i+2])
        
    marker = "o"
    if len(diff) > 200:
        marker = "."
    if not isMultiple:
        if len(diff) > 1 and stats.stdev(diff) > 0.1:
            logger.error("Why do you have a high stdev?" + str(stats.stdev(diff)))
            marker = "x"

    ax.plot_date(dates, diff, c, xdate=True, marker = marker, linestyle="", label=label)
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
    root = sys.argv[1] + "/"
    resFnList = [os.path.relpath(os.path.join(dirpath, f), root)
                    for dirpath, dirnames, files in os.walk(root)
                        for f in fnmatch.filter(files, "*.res")]
    resFnList.sort()

    dest = root + "graph/"
    if not os.path.exists(dest):
        os.makedirs(dest)

    for fn in resFnList:
        logger.info("Working on " + fn)

        #Parsing .res, the format is ID DATA DATA ... APP APP... TIME
        array = fs.readFileToArray(root + fn)
        split = [i.split()[:-1] for i in array]
        times = [i.split()[-1] for i in array]
        appertures = split[0][int((len(split[0])+1) / 2):]
        data = [[], []]

        #This creates an array in the format data[star][field][exp]
        #TODO try to optimize it for rapid memory?
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

        #Filters out the stars where DATA is INDEF
        goodStarsByExp = [[] for i in range(nbExp)]
        for exp in range(nbExp):
            for star in range(1, min(30, nbStars + 1)):
                isIndef = False
                for field in range(nbFields):
                    if isIndef or data[star][field][exp] == "INDEF":
                        isIndef = True
                        break
                if not isIndef:
                    goodStarsByExp[exp].append(star)

        #Data analysis loop
        magdifByAppStar = []
        diffDone = False
        for exp in range(nbExp):
            stars = goodStarsByExp[exp]
            #Skip if transit star isn't good
            if 1 not in stars:
                continue
            logger.debug("Working on apperture #" + str(exp))

            magdifByStar = []
            working = True
            success = False

            #Loop to eliminate bad comparison stars
            while working:
                logger.debug("New pass")
                working = False
                success = True

                if len(stars[1:]) < 1:
                    working = False
                    success = False

                dataApp = [[data[star][field][exp] for field in range(nbFields)] for star in stars]
                magdifByStar = analyzeTransitByApp(dataApp, stars)

                #Pop bad comp stars
                for i, star in enumerate(stars):
                    if len(magdifByStar[star]) <= 1:
                        break
                    stdev = stats.stdev(magdifByStar[star])
                    if star != 1 and stdev > 0.1:
                        working = True
                        stars.pop(i)
                        logger.debug("Popping " + str(star))

            #Update everything according to loop's results
            goodStarsByExp[exp] = stars
            if success:
                diffDone = True
                magdifByAppStar.append(magdifByStar)
            else:
                magdifByAppStar.append([])
                logger.debug("Apperture: " + str(exp) + " didn't work :(")

        #None of the passes worked, throw a warning :(
        if not diffDone:
            logger.warning("Sad transit: " + fn)
            continue



        ##########
        #Plotting#
        ##########
        dpi = 150

        if not os.path.exists(dest + "comp/"):
            os.makedirs(dest + "comp/")

        bfn = os.path.splitext(os.path.splitext(fn.strip("atlas_"))[0])[0]
        #Plot transits
        start, end = getTransitStartEnd(bfn)

        dates = matplotlib.dates.date2num(timestamps)
        for i in range(len(magdifByAppStar)):
            if magdifByAppStar[i] == []:
                continue
            fig, ax = plt.subplots()
            app = str(int(float(appertures[i])))
            logger.debug("Plot " + app)
            addDataToPlt(fig, ax, dates, magdifByAppStar[i][1], "c", app)
            addStartEndToPlt(ax, (start, end))
            plt.xlabel('Time')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(dest + bfn + "-" + app + ".png", dpi=dpi, bbox_extra_artists=(ax.legend,))
            plt.close()

            ##Other stars, by app
            fig, ax = plt.subplots()
            logger.debug("Plot " + app + " comparison stars")
            for star in goodStarsByExp[i]:
                if star == 1:
                    continue
                logger.debug("star " + str(star))
                addDataToPlt(fig, ax, dates, magdifByAppStar[i][star], colorList[star%7], star, False)

            sys.stdout.flush()
            plt.xlabel('Time')
            plt.ylabel('Apparent magnitude difference')
            plt.savefig(dest + "comp/" + bfn + "-" + app + ".comparison.png", dpi=dpi, bbox_extra_artists=(ax.legend,))
            plt.close()

        #Plot all transits together
        fig, ax = plt.subplots()
        logger.debug("Plot collective")
        for i in range(len(magdifByAppStar)):
            if magdifByAppStar[i] == []:
                continue
            app = str(int(float(appertures[i])))
            addDataToPlt(fig, ax, dates, magdifByAppStar[i][1], colorList[i%7], app, False)

        plt.xlabel('Timestamp (seconds)')
        plt.ylabel('Apparent magnitude difference')
        plt.savefig(dest + bfn + ".png", dpi = dpi, bbox_extra_artists=(ax.legend(),), bbox_inches='tight')
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
