import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def CalcCO2Poly(days,x2,x1,x0):
    co2calc= x2*days**2 + x1*days +x0
    return co2calc
    
dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

# Finds the earliest date and then takes the total time elapsed in days, daysSinceStart
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

CO2polyfit=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)

co2fitPoly=CalcCO2Poly(daysSinceStart,CO2polyfit[0],CO2polyfit[1],CO2polyfit[2])
ax.plot(dfCarbonDioxide['date'],co2fitPoly,'-r')

# scipy.optimize.curve_fit()




