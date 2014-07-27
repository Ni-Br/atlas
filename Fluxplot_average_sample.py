import fs
import numpy as np
import matplotlib.pyplot as plt

#For explanations of parameters and maths, see fluxplot_sample #

array = fs.readFileToArray("CoRoT2b-60.000secs.Light.R.00001523.res")
z = [i.split(" ")[4] for i in array]

for i in range(len(z)):
    if z[i] != "INDEF":
        z[i] = float(z[i])

magdif = []
t = 0
time = []
difsum = 0
count = 0
totalid = 18 #!!!INPUT!!!: total number of stars you do photometry

starlist = [1,4,5,6,7,9,10,11,12,13,14,15,16,17,18] #!!!INPUT!!!: list of all stars you want to average

t_exp = 60 #!!!INPUT!!! Exposure time

for i in range(0,int(len(z)/totalid) ):
    average = 0
    count = 0
    for j in starlist:
        val = z[i*totalid + j - 1]
        if val != "INDEF":
            average += z[i*totalid + j - 1]
            count += 1
    dif = average/count - z[i*totalid]
#   if 0.61 <= dif and dif <= 0.68:    #to set criterion, uncomment this line, and indent next TWO lines
    magdif.append(dif)
    time.append(t)
    
    t = t + t_exp +4.8
    

plt.scatter(time, magdif)
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
