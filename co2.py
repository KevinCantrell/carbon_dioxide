import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from scipy.optimize import curve_fit
from scipy import stats
 
def funcCO2(days,c2,c1,c0,amplitude,offset,period):
    co2poly=c2*days**2+c1*days+c0
    co2cos=(amplitude/2)*np.cos(((days+offset)*2*np.pi)/period)
    co2=co2poly+co2cos
    return co2

#add lines to the function that adds a sine or cosine wave to implement oscillations
#need a periodic function (high in may, low in october)
#build in information about seasonal variation

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158) #reading the connected data from NOAA
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']]) 
boolMissing=dfCarbonDioxide['value']==-999.99 #find out where we have missing data
dfCarbonDioxide[boolMissing]=np.nan #changing -999.99 to nan which is not a number
dfCarbonDioxide=dfCarbonDioxide.dropna() #dropping missing data (nan)
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True) #reindex the data (makes missing data completely disappear)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

popt,pcov=curve_fit(funcCO2,daysSinceStart,dfCarbonDioxide['value'],p0=[0.0000001055,0.00311,331,8,120,365])
#going up about 0.003 ppm/day
#amplitude=8,offset=120,period=365,c2=1.055x10^-7,c1=3.11x10^-3,c0=3.31x10^2

fitCO2=funcCO2(daysSinceStart,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
#need to change the x-value to include hypothetical co2 values
print("curve_fit parameters: ",popt)
print("curve_fit errors: ",np.sqrt(np.diag(pcov)))
co2errors=np.sqrt(np.diag(pcov))
n=len(daysSinceStart)
df=n-len(popt)
resco2=fitCO2-dfCarbonDioxide['value']
syco2=np.sqrt(np.sum(resco2**2)/df)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(daysSinceStart,resco2,'-k')







