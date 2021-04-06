import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

def fitOsc(x,amp,period,offset):
    y=amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
    #y=amp*np.cos(period*(x+offset))
    return y

def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'] )
fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

residuals=fitCO2-dfCarbonDioxide['value']
figRes,axRes=plt.subplots(figsize=(12,8))
axRes.plot(dfCarbonDioxide['date'],residuals)
axRes.plot(daysSinceStart,residuals)


stdError=np.sqrt(np.sum(residuals**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))

#pyplOscillationCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,OscillationCalc)