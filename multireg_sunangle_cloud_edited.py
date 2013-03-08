#THIS PROGRAM TAKES 4 INPUT FILES
#THIS MODULE FIRST CLASSIFIES THE WINDOW LIGHT AND INDOOR LIGHT (AT ONE SENSOR)
#BY CLOUDINESS (BINARY) AND THEN SUNANGLE (TILT) AND HOUR OF DAY (BINARY)
#CLOUDINESS IS CLOUDY OR SUNNY
#HOUR OF DAY IS AM OR PM
#THIS MODEL PERFORMS LINEAR REGRESSION BETWEEN INDIVIDUAL WORKPLANE LIGHT AND WINDOW LIGHT FOR BINS OF SUN TILT AND TIME OF DAY (LIKE am OR pm)

print "This program classifies the data first into morning and afternoon, then by a bilevel cloudiness condition, then by 5 minutes sun angle"
print "   "
print "It then spells out the coefficients of linear regression models correlating window light with indoor light level"
print "  "
print "The program takes four input datasets: window light, indoor light, sun position and cloudiness condition"

import numpy as np
import scipy as sp
from scipy import stats
from numpy import vstack
import scikits.statsmodels.api as sm
import time
import datetime
from datetime import date
import matplotlib as mpl
from matplotlib import pyplot as plt
from time import mktime, localtime, gmtime, strftime
import pdb

print "  "
sens_no=raw_input("Enter the sensor number: ")
getworkplane="C:\Users\chandrayee\Documents\NASA\ParsedData\workstation\\model\\modeltrain_1128_0113_"+str(sens_no)+"parsedfinal.txt" #INDOOR LIGHT
getdaylight="C:\Users\chandrayee\Documents\NASA\ParsedData\windowsensors\\model\\winmodeltrain_1128_0113parsedfinal"+".txt" #WINDOW LIGHT
getsunpos=open("C:\Users\chandrayee\Documents\NASA\ParsedData\sunpos_1128_0113.txt") #SUNANGLE (TILT)
getcloudiness=open("C:\Users\chandrayee\Documents\NASA\ParsedData\\berkeleyweather\cloudiness_1128_0113.txt") #CLOUDINESS (BINARY)
workplane_line_list=getworkplane.readlines()
daylight_line_list=getdaylight.readlines()
sunpos_line_list=getsunpos.readlines()
cloudiness_line_list=getcloudiness.readlines()
count=0
print "   "
print "The lengths of the datasets are ", len(workplane_line_list),len(daylight_line_list),len(sunpos_line_list),len(cloudiness_line_list)
#define local arrays
daytype=[] #MORNING OR AFTERNOON?
datamorningsunny=[]
datamorningcloudy=[]
dataafternoonsunny=[]
dataafternooncloudy=[]
sunmornsunny=[] #WHAT IS THE DIFFERENCE BETWEEN DATAMORNINGSUNNY AND SUNMORNSUNNY??
sunmorncloudy=[]
sunaftersunny=[]
sunaftercloudy=[]
amsunny=[] #WHAT ARE THESE? WHAT DO THEY STORE?
amcloudy=[]
pmsunny=[]
pmcloudy=[]
pm=[]
wstam=[]
wstpm=[]
dlttrail=[]
diflen=len(workplane_line_list)-len(daylight_line_list)
#matching data with the dataset of shortest length
if diflen>=0:
    a=len(daylight_line_list)
else:
    a=len(workplane_line_list)
print "  "
print "The length of the dataset is ",a
#arrange data in bins for hours of day, cloudiness into arrays 
for count in range(a): # THE VALUES FOR TIME (?) DON'T MATCH UP IN THE MODEL... AND WINMODEL... FILES???
    wst=str.split(workplane_line_list[count])#GETS THE LINE FROM MODEL... FILE
    dlt1=str.split(daylight_line_list[count],'\t') #GETS THE LINE FROM WINMODEL... FILE
    daylight_meas=float(str.split(dlt1[7],'\n')) #GETS THE MEASUREMENT FROM LINE 'COUNT' OF WINMODEL... FILE
    sun=str.split(sunpos_line_list[count],'\t') 
    #print dlt1
    #print wst[3],sun[3]
    #if wst[8]=="6" or wst[8]=="7":
    #if float(sun[3])-float(wst[3])==1 and abs(float(sun[4])-float(wst[4]))<=15:
    #CURRENTLY THE WINDOW LIGHT AND INDOOR LIGHT DATA HAS MORE THAN 20 MINUTES GAP WHICH MEANS THERE ARE MISSING DATA POINTS IN ONE OF THE DATA SETS
    #GET RID OF ZEROES FROM THE DATA
    if daylight_meas!=0 and float(wst[7])!=0: #wst[7] IS MEASUREMENT FROM LINE 'COUNT' OF MODEL... FILE (IF THE MEASUREMENTS EXIST..)
        #if the day, the hour and the minutes matches for the two files
        if float(dlt1[2])==float(wst[2]) and abs(float(dlt1[3])==float(wst[3])) and abs(float(dlt1[4])-float(wst[4]))<=8: #WHY USE ABS(FLOAT(DLT1[3]...)?
            #daytype.append(wst[8])
            for count in range(len(cloudiness_line_list)):
                cloud=str.split(cloudiness_line_list[count],'\t')
                #if day and hour matches
                if float(cloud[0])==float(wst[2]) and float(cloud[1])==float(wst[1]) and float(cloud[2])==float(wst[0]):
                #print cloud[4]+'    '+cloud[0]+'   '+str(float(wst[2]))
                    #classify by pm
                    if float(sun[3])>=12:
                #data contains y x and sunalt
                        #classify by cloudiness
                        if cloud[4]=='sunny':
                            #This array contains the y, x, sunposition and cloudiness values
                            dataafternoonsunny.append(wst[7]+' '+daylight_meas[0]+' '+sun[6]+' '+cloud[4]+'\n')
                            sunaftersunny.append(float(sun[6]))
                            pmsunny.append(dlt1[3]+':'+dlt1[4]+':'+dlt1[5])
                        elif cloud[4]=='cloudy':
                            dataafternooncloudy.append(wst[7]+' '+daylight_meas[0]+' '+sun[6]+' '+cloud[4]+'\n') #indoor meas, daylight meas, sunpos, cloudiness
                            sunaftercloudy.append(float(sun[6])) #sunpos
                            pmcloudy.append(dlt1[3]+':'+dlt1[4]+':'+dlt1[5]) # hour, minute, second? do you record the date?
                    #classify data by morning"
                    elif float(sun[3])<12:
                        if cloud[4]=='sunny':
                            datamorningsunny.append(wst[7]+' '+daylight_meas[0]+' '+sun[6]+' '+cloud[4]+'\n')
                            sunmornsunny.append(float(sun[6]))
                            amsunny.append(dlt1[3]+':'+dlt1[4]+':'+dlt1[5])
                        elif cloud[4]=='cloudy':
                            datamorningcloudy.append(wst[7]+' '+daylight_meas[0]+' '+sun[6]+' '+cloud[4]+'\n')
                            sunmorncloudy.append(float(sun[6]))
                            amcloudy.append(dlt1[3]+':'+dlt1[4]+':'+dlt1[5])
#print len(datamorning),len(am),len(dataafternoon),len(pm)
#This is the classified array of sun angle
sunmornsunnyarray=sp.array(sunmornsunny)
sunmorncloudyarray=sp.array(sunmorncloudy)
sunaftersunnyarray=sp.array(sunaftersunny)
sunaftercloudyarray=sp.array(sunaftercloudy)
print "  "
print "Data lengths for sunny and cloudy mornings and sunny and cloudy afternoons are ",len(sunmornsunny), len(sunmorncloudy),len(sunaftersunny), len(sunaftercloudy)
###print sunmornsunny
###print "       "
###print "       "
###print sunmorncloudy
###print "       "
###print "       "
###print sunaftersunny
###print "       "
###print "       "
###print sunaftercloudy
####
#start collecting the morning and the afternoon data separately into bins of sun tilt
print "  "
bs=raw_input("Enter the bin size of sunposition  in int: ")
#declare list of lists
x1=[[] for i in range(int(max(sunmornsunnyarray))+abs(int(min(sunmornsunnyarray))))]
y1=[[] for i in range(int(max(sunmornsunnyarray))+abs(int(min(sunmornsunnyarray))))]
x2=[[] for j in range(int(max(sunmorncloudyarray))+abs(int(min(sunmorncloudyarray))))]
y2=[[] for j in range(int(max(sunmorncloudyarray))+abs(int(min(sunmorncloudyarray))))]
x3=[[] for i in range(int(max(sunaftersunnyarray))+abs(int(min(sunaftersunnyarray))))]
y3=[[] for i in range(int(max(sunaftersunnyarray))+abs(int(min(sunaftersunnyarray))))]
x4=[[] for j in range(int(max(sunaftercloudyarray))+abs(int(min(sunaftercloudyarray))))]
y4=[[] for j in range(int(max(sunaftercloudyarray))+abs(int(min(sunaftercloudyarray))))]
s1=[[] for i in range(int(max(sunmornsunnyarray))+abs(int(min(sunmornsunnyarray))))]
s2=[[] for j in range(int(max(sunmorncloudyarray))+abs(int(min(sunmorncloudyarray))))]
t1=[[] for i in range(int(max(sunmornsunnyarray))+abs(int(min(sunmornsunnyarray))))]
t2=[[] for j in range(int(max(sunmorncloudyarray))+abs(int(min(sunmorncloudyarray))))]
s3=[[] for i in range(int(max(sunaftersunnyarray))+abs(int(min(sunaftersunnyarray))))]
s4=[[] for j in range(int(max(sunaftercloudyarray))+abs(int(min(sunaftercloudyarray))))]
t3=[[] for i in range(int(max(sunaftersunnyarray))+abs(int(min(sunaftersunnyarray))))]
t4=[[] for j in range(int(max(sunaftercloudyarray))+abs(int(min(sunaftercloudyarray))))]
#DEFINE LISTS AND FILE LOCATIONS
print "   "
print "Now we will start separating the window and indoor light data by cloudiness and time of day into bins of sun angle"
#define location of the coefficients
direc1="C:\Users\chandrayee\Documents\NASA\ParsedData\coefficients"
resfileamsunny=direc1+str(sens_no)+"\\resamsunny"+str(sens_no)+".txt"
resfilepmsunny=direc1+str(sens_no)+"\\respmsunny"+str(sens_no)+".txt"
resfileamcloudy=direc1+str(sens_no)+"\\resamcloudy"+str(sens_no)+".txt"
resfilepmcloudy=direc1+str(sens_no)+"\\respmcloudy"+str(sens_no)+".txt"
amparamsunny=open(resfileamsunny,'a')
pmparamsunny=open(resfilepmsunny,'a')
amparamcloudy=open(resfileamcloudy,'a')
pmparamcloudy=open(resfilepmcloudy,'a')
erramsunny=[]
erramcloudy=[]
errpmsunny=[]
errpmcloudy=[]
direc2="C:\Users\chandrayee\Documents\NASA\ParsedData\\classify"
##MODEL COEFFICIENTS FOR SUNNY MORNING
#break down coefficients by sun tilt
for count in range(len(datamorningsunny)):
    split=str.split(datamorningsunny[count])
    if float(split[2])>=-10:
        #Mo and Andrew helped here in constructing the loop and the dependency
        for i in range(int(max(sunmornsunnyarray))+abs(-10)):
            if int(float(split[2]))==-10+i:
                x1[i-1].append(float(split[1]))
                y1[i-1].append(float(split[0]))
                s1[i-1].append(float(split[2]))
                t1[i-1].append(amsunny[count])
#perform OLS
for i in range((int(max(sunmornsunnyarray))+abs(-10))-1):
    filename1=direc2+str(sens_no)+"\\sunny"+str(i)+"am.txt"
    savedata1=open(filename1,"a")
    for count in range(len(x1[i])):
        save1=str(round(x1[i][count],2))+'\t'+str(round(y1[i][count],2))+'\t'+str(round(s1[i][count],2))+'\t'+t1[i][count]+'\n'
        savedata1.write(save1)
    savedata1.close()
    if len(x1[i])>7 and x1[i]>0 and y1[i]>0:
        adata=vstack((y1[i],x1[i]))
        realadata=adata.transpose()
        y=realadata[:,0]
        x=realadata[:,1]
        X=sm.add_constant(x)
        model = sm.OLS(y, X)
        fitmorn=model.fit()
        diffmornsun=y-fitmorn.fittedvalues
        sunam=np.mean(s1[i])
        if len(fitmorn.params)>1:
            coeffmorn=str(i)+'\t'+str(round(fitmorn.params[0],3))+'\t'+str(round(np.mean(diffmornsun),3))+'\t'+str(round(fitmorn.params[1],3))+'\t'+str(round(fitmorn.rsquared,3))+'\t'+str(round(sunam,3))+'\t'+'am'+'\n'
        else:
            coeffmorn=str(i)+'\t'+str(round(fitmorn.params[0],3))+'\t'+str(round(np.mean(diffmornsun),3))+'\t'+"0"+'\t'+str(round(fitmorn.rsquared,3))+'\t'+str(round(sunam,3))+'\t'+'am'+'\n'
        amparamsunny.write(coeffmorn)
amparamsunny.close()
print "   "
print "Coefficients saved for sunny morning"
##MODEL COEFFICIENTS FOR CLOUDY MORNING
#Mo and Andrew helped here in constructing the loop and the dependency
for count in range(len(datamorningcloudy)):
    split=str.split(datamorningcloudy[count])
    if float(split[2])>=-10:
        for i in range(int(max(sunmorncloudyarray))+abs(-10)):
            if int(float(split[2]))==-10+i:
                x2[i-1].append(float(split[1]))
                y2[i-1].append(float(split[0]))
                s2[i-1].append(float(split[2]))
                t2[i-1].append(amcloudy[count])
#perform OLS
for i in range((int(max(sunmorncloudyarray))+abs(-10))-1):
    filename2=direc2+str(sens_no)+"\\cloudy"+str(i)+"am.txt"
    savedata2=open(filename2,"a")
    for count in range(len(x2[i])):
        save2=str(round(x2[i][count],2))+'\t'+str(round(y2[i][count],2))+'\t'+str(round(s2[i][count],2))+'\t'+t2[i][count]+'\n'
        savedata2.write(save2)
    savedata2.close()
    if len(x2[i])>7 and x2[i]>0 and y2[i]>0:
        adata=vstack((y2[i],x2[i]))
        realadata=adata.transpose()
        y=realadata[:,0]
        x=realadata[:,1]
        X=sm.add_constant(x)
        model = sm.OLS(y, X)
        fitmorn=model.fit()
        diffmorncloud=y-fitmorn.fittedvalues
        sunam=np.mean(s2[i])
        if len(fitmorn.params)>1:
            coeffmorn=str(i)+'\t'+str(round(fitmorn.params[0],3))+'\t'+str(round(np.mean(diffmorncloud),3))+'\t'+str(round(fitmorn.params[1],3))+'\t'+str(round(fitmorn.rsquared,3))+'\t'+str(round(sunam,3))+'\t'+'am'+'\n'
        else:
            coeffmorn=str(i)+'\t'+str(round(fitmorn.params[0],3))+'\t'+str(round(np.mean(diffmorncloud),3))+'\t'+"0"+'\t'+str(round(fitmorn.rsquared,3))+'\t'+str(round(sunam,3))+'\t'+'am'+'\n'
        amparamcloudy.write(coeffmorn)
amparamcloudy.close()
print "   "
print "Coefficients saved for cloudy morning"
#MODEL COEFFICIENTS FOR SUNNY AFTERNOON    
for count in range(len(dataafternoonsunny)):
    split2=str.split(dataafternoonsunny[count])
    if float(split2[2])>=-10:
        for j in range(int(max(sunaftersunnyarray))+abs(-10)):
            if int(float(split2[2]))==-10+j:
                x3[j-1].append(float(split2[1]))
                y3[j-1].append(float(split2[0]))
                s3[j-1].append(float(split2[2]))
                t3[j-1].append(pmsunny[count])
for j in range((int(max(sunaftersunnyarray))+abs(-10))-1):
    filename3=direc2+str(sens_no)+"\\sunny"+str(j)+"pm.txt"
    savedata3=open(filename3,"a")
    for count in range(len(x3[j])):
        save3=str(round(x3[j][count],2))+'\t'+str(round(y3[j][count],2))+'\t'+str(round(s3[j][count],2))+'\t'+t3[j][count]+'\n'
        savedata3.write(save3)
    savedata3.close()
    if len(x3[j])>7 and x3[j]>0 and y3[j]>0:
        adata=vstack((y3[j],x3[j]))
        realadata=adata.transpose()
        y=realadata[:,0]
        x=realadata[:,1]
        X=sm.add_constant(x)
        model = sm.OLS(y, X)
        fitafter=model.fit()
        diffaftersun=y-fitafter.fittedvalues
        sunpm=np.mean(s3[j])
        if len(fitmorn.params)>1:
            coeffafter=str(j)+'\t'+str(round(fitafter.params[0],3))+'\t'+str(round(np.mean(diffaftersun),3))+'\t'+str(round(fitafter.params[1],3))+'\t'+str(round(fitafter.rsquared,3))+'\t'+str(round(sunpm,3))+'\t'+'pm'+'\n'
        else:
            coeffafter=str(j)+'\t'+str(round(fitafter.params[0],3))+'\t'+str(round(np.mean(diffaftersun),3))+'\t'+"0"+'\t'+str(round(fitafter.rsquared,3))+'\t'+str(round(sunpm,3))+'\t'+'pm'+'\n'
        pmparamsunny.write(coeffafter)
pmparamsunny.close()
print "   "
print "Coefficients saved for sunny afternoon"
#MODEL COEFFICIENTS FOR CLOUDY AFTERNOON    
for count in range(len(dataafternooncloudy)):
    split2=str.split(dataafternooncloudy[count])
    if float(split2[2])>=-10:
        for j in range(int(max(sunaftercloudyarray))+abs(-10)):
            if int(float(split2[2]))==-10+j:
                x4[j-1].append(float(split2[1]))
                y4[j-1].append(float(split2[0]))
                s4[j-1].append(float(split2[2]))
                t4[j-1].append(pmcloudy[count])
for j in range((int(max(sunaftercloudyarray))+abs(-10))-1):
    filename4=direc2+str(sens_no)+"\\cloudy"+str(j)+"pm.txt"
    savedata4=open(filename4,"a")
    for count in range(len(x4[j])):
        save4=str(round(x4[j][count],2))+'\t'+str(round(y4[j][count],2))+'\t'+str(round(s4[j][count],2))+'\t'+t4[j][count]+'\n'
        savedata4.write(save4)
    savedata2.close()
    if len(x4[j])>7 and x4[j]>0 and y4[j]>0:
        adata=vstack((y4[j],x4[j]))
        realadata=adata.transpose()
        y=realadata[:,0]
        x=realadata[:,1]
        X=sm.add_constant(x)
        model = sm.OLS(y, X)
        fitafter=model.fit()
        diffaftercloud=y-fitafter.fittedvalues
        sunpm=np.mean(s4[j])
        if len(fitmorn.params)>1:
            coeffafter=str(j)+'\t'+str(round(fitafter.params[0],3))+'\t'+str(round(np.mean(diffaftercloud),3))+'\t'+str(round(fitafter.params[1],3))+'\t'+str(round(fitafter.rsquared,3))+'\t'+str(round(sunpm,3))+'\t'+'pm'+'\n'
        else:
            coeffafter=str(j)+'\t'+str(round(fitafter.params[0],3))+'\t'+str(round(np.mean(diffaftercloud),3))+'\t'+"0"+'\t'+str(round(fitafter.rsquared,3))+'\t'+str(round(sunpm,3))+'\t'+'pm'+'\n'
        pmparamcloudy.write(coeffafter)
pmparamcloudy.close()
getsunpos.close()
getcloudiness.close()
getdaylight.close()
getworkplane.close()
print "   "
print "Coefficients saved for cloudy afternoon"
print "    "
print "done"
