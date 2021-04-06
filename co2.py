import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

def fitOsc(x,amp,period,offset):
    y=amp/2*np.cos((x+offset)*2*np.pi/period)
    return y

def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)#reads text file and stores as a dataframe
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])#converts all of the date/time stuff to a single variable type
boolMissing=dfCarbonDioxide['value']==-999.99#boolean filter for missing data
dfCarbonDioxide[boolMissing]=np.nan#using boolean filter to take out missing values
dfCarbonDioxide=dfCarbonDioxide.dropna()#drops missing values
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)#renumbers the dataframe index without the dropped values

#makes a plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'])

#fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
fitCO2=fitAll(daysSinceStart,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

fig1,ax1=plt.subplots(figsize=(12,8))
residual=fitCO2-dfCarbonDioxide['value']
#ax1.plot(dfCarbonDioxide['date'],residual,'-g')
ax1.plot(daysSinceStart,residual)
stdError=np.sqrt(np.sum(residual**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))

oscillationCalc=fitOsc(daysSinceStart,8,365.25,200)
ax1.plot(daysSinceStart,oscillationCalc)