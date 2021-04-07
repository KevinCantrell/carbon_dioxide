# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:48:35 2021

@author: sk8er
"""
#Michelle Rodriguez
#CHM-477A
#Green House

#imports
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from scipy.optimize import curve_fit



register_matplotlib_converters()

#defining functions, given funtions
def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def FitPly(x,c0,c1,c2):
    y=c0+(x*c1)+(x**2*c2)
    return y

def FitAll(x,c0,c1,c2, amp, period, offset):
    y=c0+(x*c1)+(x**2*c2)+amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 
    return y

#reading table
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)


#removing missing data
    #missing values are given ad -999.99
boolMissing=dfCarbonDioxide['value']==-999.99
    #missing datat is replaced by nan
dfCarbonDioxide[boolMissing]=np.nan
    #remcoves data that has na values
dfCarbonDioxide=dfCarbonDioxide.dropna()
    #resets the index to account for drop
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)



#Changing Date, eliminating time specifics, and moving date to first column
    #makes the dates and time into a single output and lists it under data
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
    #removes the colums
dfCarbonDioxide=dfCarbonDioxide.drop(columns=['year', 'month', 'day','hour', 'minute', 'second'],axis=1)
    #reorganizes colums
dfCarbonDioxide=dfCarbonDioxide[["date","site_code","time_decimal",'value', 'value_std_dev', 'nvalue', 'latitude', 'longitude', 'altitude', 'elevation', 'intake_height', 'qcflag']]

#plotting data
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")

#time elapsed calculation
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

#2nd order fitting of carbon dioxide relative to days elapsed
#bettet than sciPi because it will give an exact answer rather than a search
fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)

#applies coefficients to x data
fitCO2=FitPly(daysSinceStart,fitCoeffs[2],fitCoeffs[1],fitCoeffs[0])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

#resiual plotting
fig,axResidual=plt.subplots()
residuals=dfCarbonDioxide['value']-fitCO2
axResidual.plot(daysSinceStart,residuals,'-b')
#calculating standard error
sy=np.sqrt(np.sum(residuals**2)/(len(residuals)-3))

#fitting oscillation to residuals
osc=oscFunc(daysSinceStart,8,365.25,100)
axResidual.plot(daysSinceStart,osc,'-r')

#using allFit to fit total first time
#this has been mdified to get a good estimate for which scipy can start from
allFit=FitAll(daysSinceStart,fitCoeffs[2],fitCoeffs[1],fitCoeffs[0],8,365.25,200)


#apply allFit with scipy
coefs,cov=curve_fit(FitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[2],fitCoeffs[1],fitCoeffs[0],8,365.25,200])
sciPyCoeffs=coefs
FinalOpt=FitAll(daysSinceStart,sciPyCoeffs[0],sciPyCoeffs[1],sciPyCoeffs[2],sciPyCoeffs[3],sciPyCoeffs[4],sciPyCoeffs[5])
ax.plot(dfCarbonDioxide['date'],FinalOpt,'-g')
residualsOpt=FinalOpt-dfCarbonDioxide['value']
fig,axResidualOpt=plt.subplots()
axResidualOpt.plot(daysSinceStart,residualsOpt,'-r')
syOpt=np.sqrt(np.sum(residualsOpt**2)/(len(residualsOpt)-6))
#print(syOpt)


#peronal input for specific dates
userDate=input("input date for prediction as YYYY-MM-DD:")
userDateTime=pd.to_datetime(userDate)
timeElapsedUser=(userDateTime-startDate)
daysPassedUser=timeElapsedUser.days
predictedUserInput=FitAll(daysPassedUser,sciPyCoeffs[0],sciPyCoeffs[1],sciPyCoeffs[2],sciPyCoeffs[3],sciPyCoeffs[4],sciPyCoeffs[5])
print()
print("The predicted CO2 for "+str(userDate)+"is "+str(round(predictedUserInput,2))+"ppmv")

