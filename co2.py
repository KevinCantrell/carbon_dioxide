import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def CO2func(days,c2,c1,c0):
    return c2*(days**2)+c1*days+c0

#import data and specifiy how to read data
dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#blfilter to omit data that is -999.99 which means it is a "filler" value in the data set
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)


#assigning dates as numbers/integers
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

#plotting the raw data
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

#plotting a fit
popt, pcov =curve_fit(CO2func,daysSinceStart,dfCarbonDioxide['value'])
calcCO2=CO2func(daysSinceStart,popt[0],popt[1],popt[2])
ax.plot(dfCarbonDioxide['date'],calcCO2,'r')

#standard error to adjust func




