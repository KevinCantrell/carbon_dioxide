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

#pulls data from the file, skipping to rows to get to data points
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
#setting up data point that is a combination of points reflected by time for x axis
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#setting up boolean data points for y axis of carbon value, ignoring the 999 stuff with missing data
boolMissing=dfCarbonDioxide['value']==-999.99
#creating missing data points
dfCarbonDioxide[boolMissing]=np.nan
#replace the dropped data with the missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#reindex after dropping missing data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#creating figure
fig, ax = plt.subplots(figsize=(12,8))
#plotting x and y axis (value of CO2)
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
#format x data to be year,month,day layout
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'])
#fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
fitCO2=(fitAll(daysSinceStart,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5]))
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
        
#plotting the residuals and cosine
res=fitCO2-dfCarbonDioxide['value']
figRes,axRes=plt.subplots()
axRes.plot(daysSinceStart,res)


#standard error w res plot
stdErr=np.sqrt(np.sum(res**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))

#oscillating plot
oscCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,oscCalc)

