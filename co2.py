import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def CalcCO2Poly(days,c2,c1,c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#converts time data into one parameter pandas datetime
boolMissing=dfCarbonDioxide['value']==-999.99
#-999.99 means didn't get good data that day
dfCarbonDioxide[boolMissing]=np.nan
#nan is pandas centinal value for missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#dropna gets rid of nan sets from dataframe
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)
#reindexes data


#goal is to model data with scipy curv fit to predict future
#turn data into number fisrt
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
#calculate time elapsed by subtracting minimum/start date
daysSinceStart=timeElapsed.dt.days
#gives number of days since start, x values

fitpoly=np.polyfit(daysSinceStart,dfCarbonDioxide['value'], 2)

co2fitPoly=CalcCO2Poly(daysSinceStart,fitpoly[0],fitpoly[1],fitpoly[2])

# xdata=np.linespace(np.min(daysSinceStart),np.max(daysSinceStart)+100,1000)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.plot(dfCarbonDioxide['date'], co2fitPoly, '-r')
#uses a date format for x axis