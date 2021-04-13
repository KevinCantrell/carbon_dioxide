import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y
def fitOsc(x,amp,period,offset):
    #y=amp/2*np.cos(period*(x+offset))
    y=amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
    return y
    
def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x, c2, c1, c0)+fitOsc(x,amp,period,offset)
    return y

#reads file and stores it as pd dataframe
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
#converts date and time data into datetime format
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#boolean filter for missing data
boolMissing=dfCarbonDioxide['value']==-999.99
#makes missing data non values
dfCarbonDioxide[boolMissing]=np.nan
#elliminates missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#elliminates rows that had missing data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#makes plot
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

#oscillationCalc=fitOsc(daysSinceStart,8,365.25,200)

residuals=fitCO2-dfCarbonDioxide['value']
figRes, axRes = plt.subplots(figsize=(12,8))
#axRes.plot(dfCarbonDioxide['date'],residuals,'-b')
axRes.plot(daysSinceStart,residuals,'-b')
#axRes.plot(daysSinceStart,oscillationCalc,'-r')

stdError=np.sqrt(np.sum(residuals**2)/(len(residuals)-len(fitCoeffs)))

