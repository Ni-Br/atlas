import datetime
import fs
import numpy as np
import matplotlib.pyplot as plt

colorList = ['c', 'b', 'm', 'r', 'y', 'g', 'w', 'k']
colorList+=colorList
colorList+=colorList
colorList+=colorList

array = fs.readFileToArray("CoRoT2b-60.000secs.Light.R.00001523.res")
split = [i.split()[:-1] for i in array]
times = [i.split()[-1] for i in array]
times = times[::18]
timestamps = [datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=datetime.timezone.utc).timestamp() for i in times]
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
    print(goodStars)


timeAxis = []
magDifByExp = []
for exp in range(nbExp):
    stars = goodStarsByExp[exp]
    if 1 not in stars:
        continue
    nbStars = len(stars)
    magdif = []
    for field in range(nbFields):
        photSum = 0
        for star in stars:
            val = data[star][field][exp]
            if val != "INDEF":
                photSum += float(val)
            else:
                print("INDEF!" + str(star) + " " + str(time[field]))
        magdif.append(photSum/nbStars - float(data[1][field][exp]))
    magDifByExp.append(magdif)

for i in range(len(magDifByExp)):
    plt.scatter(timestamps, magDifByExp[i], c=colorList[i])
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


plt.xlabel('time (seconds)')
plt.ylabel('apparent magnitude')
plt.show()
