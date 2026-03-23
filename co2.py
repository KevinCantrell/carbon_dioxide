import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
'''reads a local file, skips 158rows, eliminate none real numbers, recalculates the index'''
dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
''''data munging to make it usable'''
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startTime = dfCarbonDioxide['date'].min()

daysSinceStart=(dfCarbonDioxide['date']-startTime).dt.days
'''int_days = daysSinceStart.astype('timedelta64[us]').astype(int)'''
polyfit = np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)
co2 =daysSinceStart**2*polyfit[0] + polyfit[1]*daysSinceStart +polyfit[2]

ax.plot(dfCarbonDioxide['date'],co2)

co2fit = dfCarbonDioxide['value']- co2

fig2, az = plt.subplots()
az.plot(dfCarbonDioxide['date'], co2fit)