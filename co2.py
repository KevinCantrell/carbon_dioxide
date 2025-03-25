import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def funcCO2(days,c2,c1,c0):
    co2=c2**2+c1+c0
    return co2

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158) #reading the connected data from NOAA
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']]) 
boolMissing=dfCarbonDioxide['value']==-999.99 #find out where we have missing data
dfCarbonDioxide[boolMissing]=np.nan #changing -999.99 to nan which is not a number
dfCarbonDioxide=dfCarbonDioxide.dropna() #dropping missing data (nan)
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True) #reindex the data (makes missing data completely disappear)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

#startDate=min(dfCarbonDioxide['date'])
#timeElapsed=dfCarbonDioxide['date']-startDate
#daysSinceStart=timeElapsed.dt.days

#curve_fit(funcCO2,)
#popt,pcov=curve_fit(funcCO2,)













